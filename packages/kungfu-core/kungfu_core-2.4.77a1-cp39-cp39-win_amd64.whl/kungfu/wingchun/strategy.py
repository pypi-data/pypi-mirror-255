#  SPDX-License-Identifier: Apache-2.0

import asyncio
import importlib
import inspect
import functools
import kungfu
import os
import sys

from kungfu.yijinjing import time as kft
from kungfu.wingchun import constants
from kungfu.wingchun import utils
from kungfu.wingchun.constants import *

lf = kungfu.__binding__.longfist
wc = kungfu.__binding__.wingchun
yjj = kungfu.__binding__.yijinjing


class Runner(wc.Runner):
    def __init__(self, ctx, mode):
        if ctx.arguments is None:
            ctx.arguments = ""
        wc.Runner.__init__(
            self,
            ctx.runtime_locator,
            ctx.group,
            ctx.name,
            mode,
            ctx.low_latency,
            ctx.arguments,
        )
        self.ctx = ctx


class Strategy(wc.Strategy):
    def __init__(self, ctx):
        wc.Strategy.__init__(self)
        ctx.log = ctx.logger
        ctx.strftime = kft.strftime
        ctx.strptime = kft.strptime
        ctx.constants = constants
        ctx.utils = utils
        self.ctx = ctx
        self.ctx.books = {}
        self.__init_strategy(ctx.path)

    def __init_strategy(self, path):
        strategy_dir = os.path.dirname(path)
        name_no_ext = os.path.split(os.path.basename(path))
        sys.path.append(os.path.relpath(strategy_dir))
        self._module = importlib.import_module(os.path.splitext(name_no_ext[1])[0])
        self._pre_start = getattr(self._module, "pre_start", lambda ctx: None)
        self._post_start = getattr(self._module, "post_start", lambda ctx: None)
        self._pre_stop = getattr(self._module, "pre_stop", lambda ctx: None)
        self._post_stop = getattr(self._module, "post_stop", lambda ctx: None)
        self._on_trading_day = getattr(
            self._module, "on_trading_day", lambda ctx, trading_day: None
        )
        self._on_bar = getattr(self._module, "on_bar", lambda ctx, bar, location: None)
        self._on_quote = getattr(
            self._module, "on_quote", lambda ctx, quote, location: None
        )
        self._on_tree = getattr(
            self._module, "on_tree", lambda ctx, tree, location: None
        )
        self._on_entrust = getattr(
            self._module, "on_entrust", lambda ctx, entrust, location: None
        )
        self._on_transaction = getattr(
            self._module, "on_transaction", lambda ctx, transaction, location: None
        )
        self._on_order = getattr(
            self._module, "on_order", lambda ctx, order, location: None
        )
        self._on_order_action_error = getattr(
            self._module, "on_order_action_error", lambda ctx, error, location: None
        )

        self._on_trade = getattr(
            self._module, "on_trade", lambda ctx, trade, location: None
        )
        self._on_deregister = getattr(
            self._module, "on_deregister", lambda ctx, deregister, location: None
        )
        self._on_broker_state_change = getattr(
            self._module,
            "on_broker_state_change",
            lambda ctx, broker_state_update, location: None,
        )
        self._on_history_order = getattr(
            self._module, "on_history_order", lambda ctx, history_order, location: None
        )
        self._on_history_trade = getattr(
            self._module, "on_history_trade", lambda ctx, history_trade, location: None
        )
        self._on_req_history_order_error = getattr(
            self._module,
            "on_req_history_order_error",
            lambda ctx, error, location: None,
        )
        self._on_req_history_trade_error = getattr(
            self._module,
            "on_req_history_trade_error",
            lambda ctx, error, location: None,
        )
        self._on_position_sync_reset = getattr(
            self._module, "on_position_sync_reset", lambda ctx, old_book, new_book: None
        )
        self._on_asset_sync_reset = getattr(
            self._module, "on_asset_sync_reset", lambda ctx, old_asset, new_asset: None
        )
        self._on_asset_margin_sync_reset = getattr(
            self._module,
            "on_asset_margin_sync_reset",
            lambda ctx, old_asset_margin, new_asset_margin: None,
        )
        self._on_custom_data = getattr(
            self._module,
            "on_custom_data",
            lambda ctx, msg_type, data, length, location: None,
        )

    def __call_proxy(self, func, *args):
        if inspect.iscoroutinefunction(func):

            async def wrap():
                await func(*args)
                self.ctx.loop._current = None

            asyncio.ensure_future(wrap())
        else:
            func(*args)

    def __init_book(self):
        location = yjj.location(
            lf.enums.mode.LIVE,
            lf.enums.category.STRATEGY,
            self.ctx.group,
            self.ctx.name,
            self.ctx.runtime_locator,
        )
        self.ctx.book = self.ctx.wc_context.bookkeeper.get_book(location.uid)
        self.ctx.basketorder_engine = self.ctx.wc_context.basketorder_engine

    def __add_timer(self, nanotime, callback):
        def wrap_callback(event):
            self.__call_proxy(callback, self.ctx, event)

        self.ctx.wc_context.add_timer(nanotime, wrap_callback)

    def __add_time_interval(self, duration, callback):
        def wrap_callback(event):
            self.__call_proxy(callback, self.ctx, event)

        self.ctx.wc_context.add_time_interval(duration, wrap_callback)

    def __add_account(self, source, account):
        self.ctx.wc_context.add_account(source, account)

    def __get_account_book(self, source, account):
        location = yjj.location(
            lf.enums.mode.LIVE,
            lf.enums.category.TD,
            source,
            account,
            self.ctx.runtime_locator,
        )
        return self.ctx.wc_context.bookkeeper.get_book(location.uid)

    async def __async_insert_order(
        self,
        side,
        instrument_id,
        exchange_id,
        source_id,
        account_id,
        price,
        volume,
        price_type=PriceType.Any,
        status_set=None,
    ):
        if status_set is None:
            status_set = [
                OrderStatus.Filled,
                OrderStatus.PartialFilledActive,
                OrderStatus.Cancelled,
                OrderStatus.Error,
            ]
        order_id = self.ctx.insert_order(
            instrument_id,
            exchange_id,
            source_id,
            account_id,
            price,
            volume,
            price_type,
            side,
        )
        await AsyncOrderAction(self.ctx, order_id, status_set)
        return self.ctx.book.orders[order_id]

    def pre_start(self, wc_context):
        self.ctx.wc_context = wc_context
        self.ctx.now = wc_context.now
        self.ctx.add_timer = self.__add_timer
        self.ctx.add_time_interval = self.__add_time_interval
        self.ctx.subscribe = wc_context.subscribe
        self.ctx.subscribe_all = wc_context.subscribe_all
        self.ctx.add_account = self.__add_account
        self.ctx.insert_block_message = wc_context.insert_block_message
        self.ctx.insert_order = wc_context.insert_order
        self.ctx.insert_order_input = wc_context.insert_order_input
        self.ctx.insert_basket_order = wc_context.insert_basket_order
        self.ctx.insert_batch_orders = wc_context.insert_batch_orders
        self.ctx.insert_array_orders = wc_context.insert_array_orders
        self.ctx.cancel_order = wc_context.cancel_order
        self.ctx.req_history_order = wc_context.req_history_order
        self.ctx.req_history_trade = wc_context.req_history_trade
        self.ctx.update_strategy_state = wc_context.update_strategy_state
        self.ctx.is_book_held = wc_context.is_book_held
        self.ctx.is_positions_mirrored = wc_context.is_positions_mirrored
        self.ctx.is_bypass_accounting = wc_context.is_bypass_accounting
        self.ctx.bypass_accounting = wc_context.bypass_accounting
        self.ctx.hold_book = wc_context.hold_book
        self.ctx.hold_positions = wc_context.hold_positions
        self.ctx.get_account_book = self.__get_account_book
        self.ctx.req_deregister = wc_context.req_deregister
        self.ctx.get_writer = wc_context.get_writer
        self.ctx.buy = functools.partial(self.__async_insert_order, Side.Buy)
        self.ctx.sell = functools.partial(self.__async_insert_order, Side.Sell)
        self.__init_book()
        self.__call_proxy(self._pre_start, self.ctx)

    def post_start(self, wc_context):
        self.__call_proxy(self._post_start, self.ctx)

    def pre_stop(self, wc_context):
        self.__call_proxy(self._pre_stop, self.ctx)

    def post_stop(self, wc_context):
        self.__call_proxy(self._post_stop, self.ctx)

    def on_quote(self, wc_context, quote, location):
        self.__call_proxy(self._on_quote, self.ctx, quote, location)

    def on_tree(self, wc_context, tree, location):
        self.__call_proxy(self._on_tree, self.ctx, tree, location)

    def on_bar(self, wc_context, bar, location):
        self.__call_proxy(self._on_bar, self.ctx, bar, location)

    def on_entrust(self, wc_context, entrust, location):
        self.__call_proxy(self._on_entrust, self.ctx, entrust, location)

    def on_transaction(self, wc_context, transaction, location):
        self.__call_proxy(self._on_transaction, self.ctx, transaction, location)

    def on_order(self, wc_context, order, location):
        self.__call_proxy(self._on_order, self.ctx, order, location)

    def on_order_action_error(self, wc_context, error, location):
        self.__call_proxy(self._on_order_action_error, self.ctx, error, location)

    def on_trade(self, wc_context, trade, location):
        self.__call_proxy(self._on_trade, self.ctx, trade, location)

    def on_deregister(self, wc_context, deregister, location):
        self.__call_proxy(self._on_deregister, self.ctx, deregister, location)

    def on_broker_state_change(self, wc_context, broker_state_update, location):
        self.__call_proxy(
            self._on_broker_state_change, self.ctx, broker_state_update, location
        )

    def on_history_order(self, wc_context, history_order, location):
        self.__call_proxy(self._on_history_order, self.ctx, history_order, location)

    def on_history_trade(self, wc_context, history_trade, location):
        self.__call_proxy(self._on_history_trade, self.ctx, history_trade, location)

    def on_req_history_order_error(self, wc_context, error, location):
        self.__call_proxy(self._on_req_history_order_error, self.ctx, error, location)

    def on_req_history_trade_error(self, wc_context, error, location):
        self.__call_proxy(self._on_req_history_trade_error, self.ctx, error, location)

    def on_trading_day(self, wc_context, daytime):
        self.ctx.trading_day = kft.to_datetime(daytime)
        self.__call_proxy(self._on_trading_day, self.ctx, daytime)

    def on_position_sync_reset(self, wc_context, old_book, new_book):
        self.__call_proxy(self._on_position_sync_reset, self.ctx, old_book, new_book)

    def on_asset_sync_reset(self, wc_context, old_asset, new_asset):
        self.__call_proxy(self._on_asset_sync_reset, self.ctx, old_asset, new_asset)

    def on_asset_margin_sync_reset(
        self, wc_context, old_asset_margin, new_asset_margin
    ):
        self.__call_proxy(
            self._on_asset_margin_sync_reset,
            self.ctx,
            old_asset_margin,
            new_asset_margin,
        )

    def on_custom_data(self, wc_context, msg_type, data, length, location):
        self.__call_proxy(
            self._on_custom_data, self.ctx, msg_type, data, length, location
        )


class AsyncOrderAction:
    def __init__(self, ctx, order_id, status_set):
        self.ctx = ctx
        self.order_id = order_id
        self.status_set = status_set
        self.future = ctx.loop.create_future()

    def __await__(self):
        return AsyncOrderActionIter(self.ctx, self)


class AsyncOrderActionIter:
    def __init__(self, ctx, action):
        self.ctx = ctx
        self.action = action
        self.book = ctx.book

    def __iter__(self):
        return self

    def __next__(self):
        if self.action.order_id in self.book.orders:
            order = self.book.orders[self.action.order_id]
            if order.status in self.action.status_set:
                raise StopIteration
        return next(iter(self.action.future))
