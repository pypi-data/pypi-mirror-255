#  SPDX-License-Identifier: Apache-2.0

import click
import functools
import glob
import kungfu
import platform
import os
import shutil
import zipfile

from collections import deque
from datetime import datetime, timedelta
from tabulate import tabulate

from kungfu.console.commands import kfc, PrioritizedCommandGroup
from kungfu.yijinjing import LOG_PATTERN, ARCHIVE_PREFIX
from kungfu.yijinjing import journal as kfj
from kungfu.yijinjing import time as kft
from kungfu.yijinjing.log import create_logger
from kungfu.yijinjing.locator import Locator
from kungfu.yijinjing.sinks.archive import ArchiveSink
from kungfu.yijinjing.utils import prune_layout_files, prue_layout_dirs_before_timestamp


SESSION_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
FRAME_TIME_FORMAT = "%H:%M:%S.%N"
DURATION_FORMAT = "%H:%M:%S.%N"
DURATION_TZ_ADJUST = int(
    timedelta(hours=datetime.fromtimestamp(0).hour).total_seconds() * 1e9
)

lf = kungfu.__binding__.longfist
yjj = kungfu.__binding__.yijinjing
journal_command_context = kfc.pass_context(
    "logger", "location", "console_width", "console_height"
)


@kfc.group(cls=PrioritizedCommandGroup, help_priority=2)
@click.option(
    "-m", "--mode", default="*", type=click.Choice(kfj.MODES.keys()), help="mode"
)
@click.option(
    "-c",
    "--category",
    default="*",
    type=click.Choice(kfj.CATEGORIES.keys()),
    help="category",
)
@click.option("-g", "--group", type=str, default="*", help="group")
@click.option("-n", "--name", type=str, default="*", help="name")
@click.help_option("-h", "--help")
@kfc.pass_context()
def journal(ctx, mode, category, group, name):
    ctx.low_latency = False
    ctx.mode = mode
    ctx.category = category
    ctx.group = group
    ctx.name = name
    ctx.location = yjj.location(
        kfj.MODES[mode], kfj.CATEGORIES[category], group, name, ctx.runtime_locator
    )
    ctx.logger = create_logger("journal", ctx.log_level, ctx.console_location)

    (ctx.console_width, ctx.console_height) = shutil.get_terminal_size((0, 0))
    yjj.setup_log(ctx.console_location, "journal")


@journal.command()
@click.option(
    "-s",
    "--sortby",
    default="begin_time",
    type=click.Choice(
        ["begin_time", "end_time", "duration", "mode", "category", "group", "name"]
    ),
    help="sorting method",
)
@click.option("-a", "--ascending", is_flag=True, help="sorted as ascending")
@click.option(
    "-f",
    "--tablefmt",
    default="simple",
    type=click.Choice(
        ["plain", "simple", "orgtbl", "grid", "fancy_grid", "rst", "textile"]
    ),
    help="output format",
)
@journal_command_context
def sessions(ctx, sortby, ascending, tablefmt):
    all_sessions = kfj.find_sessions(ctx).sort_values(by=sortby, ascending=ascending)
    all_sessions["begin_time"] = all_sessions["begin_time"].apply(
        lambda t: kft.strftime(t, kft.SESSION_DATETIME_FORMAT)
    )
    all_sessions["end_time"] = all_sessions["end_time"].apply(
        lambda t: kft.strftime(abs(t), kft.SESSION_DATETIME_FORMAT)
    )
    all_sessions["duration"] = all_sessions["duration"].apply(
        lambda t: kft.strftime(t - kft.DURATION_TZ_ADJUST, kft.DURATION_FORMAT)
    )

    table = tabulate(
        all_sessions.values, headers=all_sessions.columns, tablefmt=tablefmt
    )

    (term_width, term_height) = shutil.get_terminal_size()
    if term_height < len(all_sessions) + 2 and platform.system() != "Windows":
        click.echo_via_pager(table)
    else:
        click.echo(table)


@journal.command()
@journal_command_context
def rebuild_index(ctx):
    io_device = yjj.io_device(ctx.console_location)
    session_builder = yjj.session_builder(io_device)
    click.echo("rebuild sqlite db")
    session_builder.rebuild_index_db()
    click.echo("done")


@journal.command()
@click.option("-i", "--session_id", type=int, required=True, help="session id")
@click.option(
    "-t",
    "--io_type",
    type=click.Choice(["all", "in", "out"]),
    default="all",
    help="input or output during this session",
)
@click.option("-o", "--csv", type=str, default="", help="csv file")
@journal_command_context
def show(ctx, session_id, io_type, csv):
    kfj.show_journal(ctx, session_id, io_type, csv)


@journal.command()
@click.option("-i", "--session_id", type=int, required=True, help="session id")
@click.option(
    "-t",
    "--io-type",
    type=click.Choice(["all", "in", "out"]),
    default="all",
    help="input or output during this session",
)
@click.option("-o", "--csv", type=str, default="", help="csv file")
@journal_command_context
def trace(ctx, session_id, io_type, csv):
    kfj.trace_journal(ctx, session_id, io_type, csv)


@journal.command()
@click.option("-A", "--archive", is_flag=True, help="archive")
@click.option("-D", "--dry", is_flag=True, help="dry run")
@journal_command_context
def clean(ctx, archive, dry):
    search_path = os.path.join(
        ctx.runtime_dir, "*", "*", "*", "journal", "*", "*.journal"
    )
    journal_files = glob.glob(search_path)
    if dry:
        for journal_file in journal_files:
            click.echo(f"rm {journal_file}")
        return
    if archive:
        datestr = kft.strfnow("%Y%m%d-%H%M%S")
        archive_path = os.path.join(ctx.home, f"KFA-{datestr}.zip")
        archive_zip = zipfile.ZipFile(
            archive_path, mode="w", compression=zipfile.ZIP_LZMA
        )
        for journal_file in journal_files:
            archive_zip.write(journal_file)
        click.echo(f"archived to {archive_path}")
    for journal_file in journal_files:
        os.remove(journal_file)
    click.echo(f"cleaned {len(journal_files)} journal files")


@journal.command()
@click.option(
    "-f",
    "--format",
    type=click.Choice(["zip", "tar"]),
    default="zip",
    help="archive format",
)
@click.option(
    "-m",
    "--mode",
    type=click.Choice(["normal", "delete"]),
    default="normal",
    help="archive mode",
)
@journal_command_context
def archive(ctx, format, mode):
    os.chdir(ctx.archive_dir)
    today_date = yjj.strftime(yjj.now_in_nano(), "%Y-%m-%d")

    if mode == "delete":
        today_start = yjj.strptime(today_date, "%Y-%m-%d")
        today_start_timestamp = today_start / 10**9
        ctx.logger.info(
            f"pruning runtime logs before {yjj.strftime(today_start, '%Y-%m-%d %H:%M:%S')}"
        )
        prue_layout_dirs_before_timestamp(
            ctx.runtime_dir, "log", "live", today_start_timestamp
        )
        ctx.logger.info(
            f"pruning runtime journals before {yjj.strftime(today_start, '%Y-%m-%d %H:%M:%S')}"
        )
        prue_layout_dirs_before_timestamp(
            ctx.runtime_dir, "journal", "live", today_start_timestamp
        )
        ctx.logger.info("archive done (delete mode)")
        return

    today_archive_name = f"{ARCHIVE_PREFIX}-{today_date}.{format}"
    today_archive_path = os.path.join(ctx.archive_dir, today_archive_name)
    today_temp_path = os.path.join(ctx.archive_dir, ".today")

    ctx.logger.info("preparing archive folder")
    deque(map(shutil.rmtree, filter(os.path.isdir, os.listdir(os.curdir))))

    if os.path.exists(today_archive_path):
        shutil.unpack_archive(today_archive_path, today_temp_path)
        export_logs(ctx, today_temp_path, ctx.archive_dir)
    else:
        os.makedirs(today_temp_path)

    ctx.logger.info("exporting journals")
    yjj.assemble([ctx.runtime_locator, Locator(today_temp_path)]) >> ArchiveSink(ctx)
    shutil.rmtree(today_temp_path)

    ctx.logger.info("exporting logs")
    export_logs(ctx, ctx.runtime_dir, ctx.archive_dir)

    ctx.logger.info("compressing archive files")
    deque(
        map(
            functools.partial(make_archive, ctx, format),
            filter(os.path.isdir, sorted(os.listdir(os.curdir))),
        )
    )

    ctx.logger.info("pruning runtime logs")
    prune_layout_files(ctx.runtime_dir, "log", "live")
    ctx.logger.info("pruning runtime journals")
    prune_layout_files(ctx.runtime_dir, "journal", "live")

    if os.path.exists(today_archive_path):
        shutil.unpack_archive(today_archive_path, ctx.runtime_dir)
    ctx.logger.info("archive done")


@journal.command("list-archive")
@journal_command_context
def list_archive(ctx):
    deque(map(print_archive, glob.glob(os.path.join(ctx.archive_dir, "*.zip"))))


def export_logs(ctx, src_dir, dst_dir):
    search_path = os.path.join(src_dir, "*", "*", "*", "log", "live", "*.log")
    for log_file in glob.glob(search_path):
        match = LOG_PATTERN.match(log_file[len(src_dir) + 1 :])
        if match:
            category = match.group(1)
            group = match.group(2)
            name = match.group(3)
            mode = match.group(4)
            date = match.group(6)
            archive_path = os.path.join(
                dst_dir, date, category, group, name, "log", mode
            )
            if not os.path.exists(archive_path):
                os.makedirs(archive_path)
            archive_log = os.path.join(archive_path, os.path.basename(log_file))
            if os.path.exists(archive_log):
                with open(log_file, "rb") as src, open(archive_log, "ab") as dst:
                    shutil.copyfileobj(src, dst)
            else:
                shutil.copy2(log_file, archive_path)
        else:
            ctx.logger.warn(f"unable to match log file {log_file}")


def make_archive(ctx, archive_format, archive_date):
    archive_locator = Locator(archive_date)
    index_location = yjj.location(
        lf.enums.mode.LIVE,
        lf.enums.category.SYSTEM,
        "journal",
        "index",
        archive_locator,
    )
    io_device = yjj.io_device(index_location, True, True)
    session_builder = yjj.session_builder(io_device)
    session_builder.rebuild_index_db()
    archive_name = f"{ARCHIVE_PREFIX}-{archive_date}"
    archive_file = f"{archive_name}.{archive_format}"
    if os.path.exists(archive_file):
        ctx.logger.warn(f"removed duplicated {archive_file}")
        os.remove(archive_file)
    shutil.make_archive(archive_name, archive_format, archive_date)
    shutil.rmtree(archive_date)
    ctx.logger.info(f"compressed archive for {archive_date}")


def print_archive(archive_file):
    archive_name = os.path.basename(archive_file)
    print(archive_name[4:-4])
