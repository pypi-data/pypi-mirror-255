<%page args="step"/>

<%
    from attune_project_api.items.step_tuples.step_tuple import (
        StepTupleTypeEnum,
    )

    from attune_project_api.items.step_tuples.step_ssh_tuple import (
        stepSshIntBash,
        stepSshIntPython,
        stepSshIntPerl,
    )
    from attune_project_api.items.step_tuples.step_winrm_tuple import (
        winCmdIntPowershellScript
    )
    from attune_project_api.items.step_tuples.step_winrm_tuple import (
        winCmdIntBatchScript
    )
    from attune_project_api.items.step_tuples.step_winrm_tuple import (
        winCmdIntCustom
    )

    if step.type in (StepTupleTypeEnum.SQL_ORACLE.value,):
        Lexer = SqlLexer

    elif step.type in (StepTupleTypeEnum.SSH.value, StepTupleTypeEnum.SSH_PROMPTED.value):
        Lexer = {stepSshIntBash.id : BashLexer,
        stepSshIntPerl.id: PerlLexer,
        stepSshIntPython.id : PythonLexer}[step.interpreter]

    elif step.type in (StepTupleTypeEnum.WINRM.value,):
        Lexer = {
            winCmdIntPowershellScript.id : PowerShellLexer,
            winCmdIntBatchScript.id: BatchLexer,
            winCmdIntCustom.id: BatchLexer
        }[step.interpreter]

    hcpLang = {BashLexer : "bash",
        PerlLexer : "bash",
        PythonLexer : "python",
        PowerShellLexer : "powershell",
        BatchLexer : "batch",
        SqlLexer : "sql",
        }.get(Lexer, "plain")

    script = step.sql if step.type == StepTupleTypeEnum.SQL_ORACLE.value else step.script

    script = script.strip()

    import html
    htmlEscapedScript = html.escape(script)

    promptResponses = [
        (r+'===').split('===')[0:2]
        for r in step.promptResponses.split ('\n')
    ] if getattr(step, "promptResponses", None) else ''
%>

    <div class="row">
        <p>
            Execute the following script:
        </p>
    </div>
    <div class="row">
        <div class="col px-0">
            <pre>
                <code class="language-${hcpLang} py-0">
${htmlEscapedScript}
                </code>
            </pre>
        </div>
    </div>

% if promptResponses:
    <div class="row">
        <p>
            This script may require you to answer the following prompts:
        </p>
    </div>
    <div class="row">
        <table>
            <thead>
                <tr>
                    <th>
                        Prompt
                    </th>
                    <th class="prompts">
                        Answer
                    </th>
                </tr>
            </thead>
            <tbody>
                % for prompt, answer in promptResponses:
                    % if prompt != '':
                <tr>
                    <td>
                        ${prompt}
                    </td>
                    <td class="prompts">
                        <code class="language-${hcpLang}">
${answer}
                        </code>
                    </td>
                </tr>
                    % endif
                % endfor
            </tbody>
        </table>
    </div>
% endif
