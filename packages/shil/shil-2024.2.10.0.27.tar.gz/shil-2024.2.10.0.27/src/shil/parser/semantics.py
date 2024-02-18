""" shil.parser.semantics
"""

import json
from pathlib import Path

from fleks.util import lme

LOGGER = lme.get_logger(__name__)


class Semantics:
    def strict_word(self, ast):
        LOGGER.info(f"strict_word: {ast}")
        return ast

    def dquote(self, ast):
        LOGGER.info(f"dquote: {ast}")
        if len(ast) > 10:
            ast = ast.lstrip()
            return f'"\\n{ast}\\n"'
        return ast

    def squote(self, ast):
        LOGGER.info(f"squote: {ast}")
        ast = ast.strip().lstrip()
        is_json = ast.startswith("{") and ast.strip().endswith("}")
        if is_json:
            try:
                tmp = json.loads(ast)
            except:
                is_json = False
            else:
                LOGGER.info(f"found json: {tmp}")
                ast = json.dumps(tmp, indent=2)
            out = [x + " \\" for x in ast.split("\n")]
            out = "\n".join(out)
            return f"'{out}'"
        return ast

    def word(self, ast):
        LOGGER.info(f"word: {ast}")
        return ast

    def simple_command(self, ast):
        LOGGER.info(f"simple_command: {ast}")
        tail = ast
        biggest = ""
        for i, l in enumerate(tail):
            if len(l) > len(biggest):
                biggest = l
        result = []
        skip_next = False
        for i, l in enumerate(tail):
            if skip_next:
                skip_next = False
                continue
            try:
                n = tail[i + 1]
            except:
                n = ""
                # LOGGER.info(f'looking at {[i,l,n]}')
            comb = f"{l} {n}"
            if len(comb) < len(biggest):
                result.append(comb)
                skip_next = True
            else:
                result.append(l)

        newp = []
        while result:
            item = result.pop(0)
            if isinstance(item, (tuple,)):
                item = " ".join(item)
            newp.append(item)
        result = newp
        # import sys
        # with open('/dev/ttys000') as user_tty:
        #     sys.stdin=user_tty
        #     import IPython; IPython.embed()
        return "\n  ".join(map(str, result))

    def shell_command(self, ast):
        LOGGER.info(f"shell_command: {ast}")
        return ast

    def path(self, ast):
        LOGGER.info(f"path: {ast}")
        try:
            tmp = Path(ast).relative_to(Path(".").absolute())
        except ValueError:
            return ast
        else:
            return f"'{tmp}'"

    def simple_command_element(self, ast):
        LOGGER.info(f"simple_command_element: {ast}")
        return ast

    def pipeline_command(self, ast):
        LOGGER.info(f"pipeline_command: {ast}")
        return ast

    def simple_list(self, ast):
        LOGGER.info(f"simple_list: {ast}")
        return ast

    def word_list(self, ast):
        LOGGER.info(f"word_list: {ast}")
        return ast

    def opt(self, ast):
        LOGGER.info(f"opt: {ast}")
        return ast if isinstance(ast, (str,)) else " ".join(ast)

    def opt_val(self, ast):
        LOGGER.info(f"opt_val: {ast}")
        return ast

    def subcommands(self, ast):
        LOGGER.info(f"subcommands: {ast}")
        return " ".join(ast)

    def drilldown(self, ast):
        LOGGER.info(f"drilldown: {ast}")
        return ast

    def entry(self, ast):
        LOGGER.info(f"entry: {ast}")
        return str(ast)
