# Copyright (c) 2021 Henix, Henix.fr
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Toolkit helpers for channels plugins."""


from typing import Any, Dict, List, Optional, Tuple, Union

from shlex import quote

import base64
import ntpath
import os
import re

from opentf.commons import EXECUTIONRESULT, make_event, make_uuid
from opentf.toolkit import core

## workflow commands

SETOUTPUT_COMMAND = re.compile(r'^::set-output\s+name=([a-zA-Z_][a-zA-Z0-9_-]*)::(.*)$')
ATTACH_COMMAND = re.compile(r'^::attach(\s+.*?)?::(.*?)\s*$')
DEBUG_COMMAND = re.compile(r'^::debug::(.*)$')
WARNING_COMMAND = re.compile(r'^::warning(\s+(.*)+)?::(.*)$')
ERROR_COMMAND = re.compile(r'^::error(\s+(.*)+)?::(.*)$')
STOPCOMMANDS_COMMAND = re.compile(r'^::stop-commands::(\w+)$')
ADDMASK_COMMAND = re.compile(r'^::add-mask::(.*)$')
PUT_FILE_COMMAND = re.compile(r'^::put file=(.*?)\s*::(.*?)\s*$')


## step sequence IDs

CHANNEL_REQUEST = -1
CHANNEL_RELEASE = -2
CHANNEL_NOTIFY = -3

DEFAULT_CHANNEL_LEASE = 60  # how long to keep the offer, in seconds

## shells

# For cmd:
#
# - /D: ignore registry autorun commands
# - /E:ON: enable command extensions
# - /V:OFF: disable delayed environment expansion
# - /S: strip " quote characters from command
# - /C: run command then terminate
#
# For bash:
#
# - --noprofile: ignore /etc/profile & al.
# - --norc: ignore /etc/bash.bashrc & al.
# - -e: exit at first error
# - -o pipefail: exit if one of the commands in the pipe fails

SHELL_DEFAULT = {'linux': 'bash', 'macos': 'bash', 'windows': 'cmd'}
SHELL_TEMPLATE = {
    'bash': 'bash --noprofile --norc -eo pipefail {0}',
    'cmd': '%ComSpec% /D /E:ON /V:OFF /S /C "CALL {0}"',
    'python': 'python {0}',
    'powershell': '''powershell -command ". './{0}'"''',
    'pwsh': '''pwsh -command ". './{0}'"''',
}

SCRIPTPATH_DEFAULT = {'linux': '/tmp', 'macos': '/tmp', 'windows': '%TEMP%'}
SCRIPTFILE_DEFAULT = {
    'linux': '{root}/{job_id}_{step_sequence_id}.sh',
    'macos': '{root}/{job_id}_{step_sequence_id}.sh',
    'windows': '{root}\\{job_id}_{step_sequence_id}.cmd',
}

LINESEP = {'linux': '\n', 'macos': '\n', 'windows': '\r\n'}
RUNNER_OS = {'windows', 'macos', 'linux'}

WORKSPACE_TEMPLATE = {
    'linux': '`pwd`/{workspace}',
    'macos': '`pwd`/{workspace}',
    'windows': '%CD%\\{workspace}',
}
VARIABLES_TEMPLATE = {
    'linux': '{root}/{job_id}_dynamic_env.sh',
    'macos': '{root}/{job_id}_dynamic_env.sh',
    'windows': '{root}\\{job_id}_dynamic_env.cmd',
}

PROLOG_SCRIPTS = {
    'windows': (
        'call "%OPENTF_VARIABLES%"',
        '@start /b cmd /c "@timeout /T 2 >nul & @del /q "{root}\\{job_id}_*.cmd""',
        # '@del /q "{root}\\{job_id}_*.cmd"',
        '@if "%OPENTF_WORKSPACE:~-2,2%" NEQ "\\." (@if exist "%OPENTF_WORKSPACE%" @rmdir /s/q "%OPENTF_WORKSPACE%")',
        '@cd "%OPENTF_WORKSPACE%"',
    ),
    'linux': (
        '. "$OPENTF_VARIABLES"',
        'rm "{root}/{job_id}"_*.sh',
        'if [[ ${OPENTF_WORKSPACE} && "${OPENTF_WORKSPACE: -2}" != "/." ]]; then rm -rf "$OPENTF_WORKSPACE"; fi',
        'cd "$OPENTF_WORKSPACE"',
    ),
    'macos': (
        '. "$OPENTF_VARIABLES"',
        'rm "{root}/{job_id}"_*.sh',
        'if [[ ${OPENTF_WORKSPACE} && "${OPENTF_WORKSPACE: -2}" != "/." ]]; then rm -rf "$OPENTF_WORKSPACE"; fi',
        'cd "$OPENTF_WORKSPACE"',
    ),
}

LOAD_VARIABLES = 0
REMOVE_SCRIPTS = 1
REMOVE_WORKSPACE = 2
MOVE_TO_WORKSPACE = 3

HOOKS_ANNOTATIONS = 'opentestfactory.org/hooks'

## os helpers


def make_variable_linux(name: str, variable: Union[str, Dict[str, Any]]) -> str:
    """Prepare variable declaration for linux runners."""

    def pseudoquote(val):
        if '"' in val:
            val = val.replace('"', '\\"')
        if ' ' in val or '\t' in val:
            val = f'"{val}"'
        return val

    if isinstance(variable, dict):
        value = variable['value']
        if variable.get('verbatim'):
            value = quote(value)
        else:
            value = pseudoquote(value)
    else:
        value = pseudoquote(variable)
    return f'export {name}={value}'


def make_variable_windows(name: str, variable: Union[str, Dict[str, Any]]) -> str:
    """Prepare variable declaration for windows runners."""
    if isinstance(variable, dict):
        value = variable['value']
        if variable.get('verbatim'):
            for symbol in '^&<>':
                value = value.replace(symbol, f'^{symbol}')
            value = value.replace('%', '%%')
    else:
        value = variable
    return f'@set "{name}={value}"'


def _add_default_variables(
    script: List[str], job_id: str, runner_os: str, root: str
) -> None:
    """Prepare default variables."""

    script.append(
        VARIABLE_MAKER[runner_os](
            'OPENTF_VARIABLES',
            VARIABLES_TEMPLATE[runner_os].format(job_id=job_id, root=root),
        )
    )
    script.append(VARIABLE_MAKER[runner_os]('OPENTF_ACTOR', 'dummy'))
    script.append(VARIABLE_MAKER[runner_os]('CI', 'true'))


def _make_attachment_url(
    metadata, remote: str, separator: str
) -> Tuple[str, Dict[str, Any]]:
    uuid = make_uuid()
    url = f'/tmp/{metadata["job_id"]}-{uuid}_{metadata["step_sequence_id"]}_{remote.split(separator)[-1]}'
    return url, {'uuid': uuid}


def _as_log(line, jobstate):
    if wcmd := DEBUG_COMMAND.match(line):
        return f'DEBUG,{mask(wcmd.group(1), jobstate)}'
    if wcmd := WARNING_COMMAND.match(line):
        return f'WARNING,{mask(wcmd.group(3), jobstate)}'
    if wcmd := ERROR_COMMAND.match(line):
        return f'ERROR,{mask(wcmd.group(3), jobstate)}'
    return mask(line, jobstate).rstrip()


## masks helpers


class JobState:
    def __init__(self) -> None:
        self.stop_command: Optional[str] = None
        self.masks = []


def mask(line: str, state) -> str:
    """Remove masked values."""
    for masked in state.masks:
        line = line.replace(masked, '***')
    return line


def process_output(
    event,
    resp: int,
    stdout: List[str],
    stderr: List[str],
    jobstate: JobState,
    _get,
    _put,
):
    """Process output, filling structures.

    # Required parameters

    - event: an ExecutionCommand event
    - resp: an integer
    - stdout: a list of strings
    - stderr: a list of strings
    - jobstate: a JobState object
    - attach: a function copying a remote file to a local path
    - put: a function copying a local file to a remote environment

    # Returned value

    An ExecutionResult event.

    # Functions arguments

    ## get

    - destination_url: a string
    - remote_path: a string (file location on execution environment)

    May raise exceptions.

    ## put

    - remote_path: a string (file location on execution environment)
    - source_url: a string

    May raise exceptions.
    """

    def _attach(remote, args):
        if is_windows:
            remote = ntpath.normpath(remote)
        try:
            attachment_url, details = _make_attachment_url(metadata, remote, separator)
            if args:
                for parameter in args.strip().split(','):
                    if '=' not in parameter:
                        logs.append(
                            f'ERROR,Invalid workflow command parameter: {parameter}.'
                        )
                        return 2
                    key, _, value = parameter.strip().partition('=')
                    details[key] = value
            _get(remote, attachment_url)
            attachments_metadata[attachment_url] = details
            attachments.append(attachment_url)
            return resp
        except Exception as err:
            logs.append(f'ERROR,Could not read {remote}: {err}.')
            return 2

    def _putfile(remote_path, data):
        working_directory = core.join_path(
            metadata['job_id'], event.get('working-directory'), is_windows
        )
        targeted_remote_path = core.join_path(
            working_directory, remote_path, is_windows
        )
        try:
            file_ = f'/tmp/in_{metadata["workflow_id"]}_{data}'
            if not os.path.exists(file_):
                logs.append(f'ERROR,Invalid resources.files reference {data}.')
                return 2
            _put(targeted_remote_path, file_)
            return resp
        except Exception as err:
            logs.append(
                f'ERROR,Could not send file {data} to remote path {remote_path}: {err}.'
            )
            return 2

    metadata = event['metadata']
    is_windows = metadata['channel_os'] == 'windows'
    separator = '\\' if is_windows else '/'
    outputs = {}
    logs = []
    attachments = []
    attachments_metadata = {}

    for line in stdout:
        # Parsing stdout for workflow commands
        if jobstate.stop_command:
            if line == jobstate.stop_command:
                jobstate.stop_command = None
            continue

        if wcmd := ATTACH_COMMAND.match(line):
            resp = _attach(wcmd.group(2), wcmd.group(1))
        elif wcmd := PUT_FILE_COMMAND.match(line):
            resp = _putfile(wcmd.group(2), wcmd.group(1))
        elif wcmd := SETOUTPUT_COMMAND.match(line):
            outputs[wcmd.group(1)] = wcmd.group(2)
        elif wcmd := STOPCOMMANDS_COMMAND.match(line):
            jobstate.stop_command = f'::{wcmd.group(1)}::'
        elif wcmd := ADDMASK_COMMAND.match(line):
            jobstate.masks.append(wcmd.group(1))
        else:
            logs.append(_as_log(line, jobstate))

    for line in stderr:
        logs.append(mask(line, jobstate).rstrip())

    result = make_event(EXECUTIONRESULT, metadata=metadata, status=resp)
    if outputs:
        result['outputs'] = outputs
    if logs:
        result['logs'] = logs
    if attachments:
        result['attachments'] = attachments
        result['metadata']['attachments'] = attachments_metadata

    return result


def _export_opentf_workspace(runner_os: str, workspace: str, script: List[str]) -> None:
    opentf_workspace = WORKSPACE_TEMPLATE[runner_os].format(workspace=workspace)
    if runner_os == 'windows':
        script.append('@type nul >>"%OPENTF_VARIABLES%"')
        script.append(
            f'@echo set "OPENTF_WORKSPACE={opentf_workspace}" >>"%OPENTF_VARIABLES%"'
        )
    else:
        script.append('touch "$OPENTF_VARIABLES"')
        script.append(
            f'echo export OPENTF_WORKSPACE="{opentf_workspace}" >> "$OPENTF_VARIABLES"'
        )


def _create_workspace(runner_os: str, workspace: str, script: List[str]) -> None:
    if runner_os == 'windows':
        script.append(f'@if not exist {workspace} @mkdir {workspace}')
    else:
        script.append(f'mkdir -p {workspace}')
    _export_opentf_workspace(runner_os, workspace, script)


def _must_keep_workspace(metadata: Dict[str, Any]) -> bool:
    hooks_annotations = metadata.get('annotations', {}).get(HOOKS_ANNOTATIONS, {})
    if hooks_annotations.get('channel') == 'teardown':
        return hooks_annotations.get('keep-workspace')
    return False


def _maybe_change_directory(
    command: Dict[str, Any], runner_os: str, script: List[str], prefix: str
) -> None:
    if 'working-directory' not in command:
        return
    path = command['working-directory']
    if runner_os == 'windows':
        path = path.replace('/', '\\')
    if ' ' in path:
        path = '"' + path.strip('"') + '"'
    script.append(f'{prefix}cd {path}')


def _maybe_create_workspace(
    metadata: Dict[str, Any], runner_os: str, step_sequence_id: int, script: List[str]
) -> None:
    hooks_annotations = metadata.get('annotations', {}).get(HOOKS_ANNOTATIONS, {})
    if hooks_annotations.get('channel') == 'setup':
        if workspace := hooks_annotations.get('use-workspace'):
            _create_workspace(runner_os, workspace, script)
            if runner_os == 'windows':
                script.append(
                    f'@echo Using workspace \'{workspace}\' on execution environment'
                )
            else:
                script.append(
                    f'echo "Using workspace \'{workspace}\' on execution environment"'
                )
        elif step_sequence_id == 0:
            _export_opentf_workspace(runner_os, '.', script)
    elif step_sequence_id == 0:
        _create_workspace(runner_os, metadata['job_id'], script)


def _make_prolog(
    runner_os: str,
    job_id: str,
    step_sequence_id: int,
    root: str,
    script: List[str],
    command: Dict[str, Any],
) -> None:
    for name, value in command.get('variables', {}).items():
        script.append(VARIABLE_MAKER[runner_os](name, value))

    script.append(PROLOG_SCRIPTS[runner_os][LOAD_VARIABLES])
    if step_sequence_id == CHANNEL_RELEASE:
        # on windows, the script ends if it is removed, so script
        # removal should be the last operation
        if not _must_keep_workspace(command['metadata']):
            script.append(PROLOG_SCRIPTS[runner_os][REMOVE_WORKSPACE])
        else:
            if runner_os == 'windows':
                script.append(
                    '@echo Keeping workspace \'%OPENTF_WORKSPACE%\' on execution environment'
                )
            else:
                script.append(
                    'echo "Keeping workspace \'$OPENTF_WORKSPACE\' on execution environment"'
                )

        script.append(
            PROLOG_SCRIPTS[runner_os][REMOVE_SCRIPTS].format(root=root, job_id=job_id)
        )
    else:
        script.append(PROLOG_SCRIPTS[runner_os][MOVE_TO_WORKSPACE])


def _make_altshell_script(
    command: Dict[str, Any], path: str, runner_os: str
) -> List[str]:
    shell = command['shell']
    marker = make_uuid()
    shell_script = command['scripts']
    if shell in ('powershell', 'pwsh'):
        path += '.ps1'
        shell_script = (
            ["$ErrorActionPreference = 'stop'"]
            + shell_script
            + [
                'if ((Test-Path -LiteralPath variable:\\LASTEXITCODE)) { exit $LASTEXITCODE }'
            ]
        )
    content = LINESEP[runner_os].join(shell_script)
    if runner_os == 'windows':
        encoded = str(base64.b64encode(bytes(content, 'utf8')), 'utf8')
        what = f'@echo {encoded} > {marker} & @certutil -f -decode {marker} {path} >nul & @del {marker}'
    else:
        what = f'cat << "{marker}" > {path}\n{content}\n{marker}'
    if runner_os == 'windows' and shell == 'bash':
        shell_command = (
            '%USERPROFILE%\\AppData\\Local\\Programs\\Git\\bin\\'
            + SHELL_TEMPLATE[shell]
        )
    else:
        shell_command = SHELL_TEMPLATE.get(shell, shell)
    return [what, shell_command.format(path)]


def make_script(
    command, script_path: Optional[str], runner_os: str
) -> Tuple[str, str, str]:
    """Prepare script.

    # Required parameters

    - command: an ExecutionCommand event
    - script_path: a string or None, where to put script on runner
    - runner_os: a string

    # Returned value

    script_path, script_content, script_command.
    """
    metadata = command['metadata']
    job_id = metadata['job_id']
    step_sequence_id = metadata['step_sequence_id']
    root = script_path or SCRIPTPATH_DEFAULT[runner_os]
    script_path = SCRIPTFILE_DEFAULT[runner_os].format(
        root=root, job_id=job_id, step_sequence_id=step_sequence_id
    )
    script_command = SHELL_TEMPLATE[SHELL_DEFAULT[runner_os]].format(f'"{script_path}"')

    script = []
    if runner_os == 'windows':
        script.append('@echo off')
        prefix = '@'
    else:
        script.append('#!/usr/bin/env bash')
        prefix = ''

    _add_default_variables(script, job_id, runner_os, root)

    _maybe_create_workspace(metadata, runner_os, step_sequence_id, script)
    _make_prolog(runner_os, job_id, step_sequence_id, root, script, command)
    _maybe_change_directory(command, runner_os, script, prefix)

    if command.get('shell') in (None, SHELL_DEFAULT[runner_os]):
        script += command['scripts']
    else:
        script += _make_altshell_script(
            command, f'{job_id}_shell_script_{step_sequence_id}', runner_os
        )

    return script_path, LINESEP[runner_os].join(script), script_command


VARIABLE_MAKER = {
    'linux': make_variable_linux,
    'macos': make_variable_linux,
    'windows': make_variable_windows,
}
