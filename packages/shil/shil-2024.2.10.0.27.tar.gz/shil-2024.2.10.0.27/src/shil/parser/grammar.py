""" shil.grammar
"""

GRAMMAR = r"""@@grammar::bash
@@comments :: /\(\*.*?\*\)/
@@eol_comments :: /#.*?$/
@@whitespace :: /[\t \n \\]/
@@keyword :: do done for in
#
# adapted from:
#   https://raw.githubusercontent.com/cbeust/kash/master/src/main/resources/bash.ebnf
#
start = pipeline_command $ | '|' pipeline_command;
do='do';
done='done';
for='for';
in ='in';
digit=/\d/;
number=/(\d)+/;
letter=/\w/;
strict_word = ?"[^-]([\w][.])+";
path=?"[^-\>][^ \t\n\r\f\v\|\<\>]+" | ?"[./\*]";
word = qblock
    | strict_word
    | path ;
_opt = ?"-[^ \t\n\r\f\v\|\<\>]+";
opt_val = ?"[^-]([\S])+";
opt = _opt word | _opt path | _opt;
word_list = {word};
assignment_word = word '=' word;
backtick = /`(.*)`/; squote = /'(.*)'/; dquote = /"(.*)"/;
qblock = backtick | squote |dquote;

redirection='>' word
    | '|' word
    | '<' word
    | number '>' word
    | number '<' word
    | '>>' word
    | number '>>' word
    | '<<' word
    | number '<<' word
    | '<&' number
    | number '<&' number
    | '>&' number
    | number '>&' number
    | '<&' word
    | number '<&' word
    | '>&' word
    | number '>&' word
    | '<<-' word
    | number '<<-' word
    | '>&' '-'
    | number '>&' '-'
    | '<&' '-'
    | number '<&' '-'
    | '&>' word
    | number '<>' word
    | '<>' word
    | '>|' word
    | number '>|' word;
simple_command= {simple_command_element}
    # |
;
# subcommands = {word};
entry=word;
simple_command_element = word
    | opt
    | assignment_word
    | redirection;
redirection_list=redirection
    |  redirection_list redirection;
subcommands={word};
drilldown=entry {subcommands} {simple_command};
command= drilldown
    | simple_command
    |  shell_command
    |  shell_command redirection_list
    ;
shell_command= for_command
  # |  case_command
  # |  while compound_list do compound_list done
  # |  until compound_list do compound_list done
  # |  select_command
  # |  if_command
    |  subshell
    |  group_command
  # |  function_def
;
for_command=for word newline_list do compound_list done
    | for word newline_list '{' compound_list '}'
    | for word ';' newline_list do compound_list done
    | for word ';' newline_list '{' compound_list '}'
    | for word newline_list in word_list list_terminator newline_list do compound_list done
    | for word newline_list in word_list list_terminator newline_list '{' compound_list '}'
;
# select_command=  select word newline_list do list done
#                |  select word newline_list '{' list '}'
#                |  select word ';' newline_list do list done
#                |  select word ';' newline_list '{' list '}'
#                |  select word newline_list in word_list
#                        list_terminator newline_list do list done
#                |  select word newline_list in word_list
#                        list_terminator newline_list '{' list '}'
# case_command=  case word newline_list in newline_list esac
#              |  case word newline_list in <case_clause_sequence>
#                      newline_list esac
#              |  case word newline_list in <case_clause> esac
# function_def=  word '(' ')' newline_list <group_command>
#              |  function word '(' ')' newline_list <group_command>
#              |  function word newline_list <group_command>
subshell=  '(' compound_list ')';
group_command=  '{' list '}';
# if_command= if compound_list then compound_list fi
#       | if compound_list then compound_list else compound_list fi
#       | if compound_list then compound_list <elif_clause> fi
# elif_clause= elif compound_list then compound_list
#        | elif compound_list then compound_list else compound_list
#        | elif compound_list then compound_list <elif_clause>
# case_clause=  <pattern_list>
#             |  <case_clause_sequence> <pattern_list>
# pattern_list=  newline_list pattern ')' compound_list
#              |  newline_list pattern ')' newline_list
#              |  newline_list '(' pattern ')' compound_list
#              |  newline_list '(' pattern ')' newline_list
# case_clause_sequence=  <pattern_list> ';;'
#                      |  <case_clause_sequence> <pattern_list> ';;'
# pattern=  word
#         |  pattern '|' word
list=   newline_list list0;
compound_list=list |  newline_list list1;
list0=   list1 '\n' newline_list
   |  list1 '&' newline_list
   |  list1 ';' newline_list
;
list1= list1 '&&' newline_list list1
   |  list1 '||' newline_list list1
   |  list1 '&' newline_list list1
   |  list1 ';' newline_list list1
   |  list1 '\n' newline_list list1
   |  pipeline_command
;
list_terminator= '\n' |  ';';
newline_list= '\n' | newline_list '\n';
simple_list=  simple_list1
    |  simple_list1 '&'
    |  simple_list1 ';'
;
simple_list1=  simple_list1 '&&' newline_list simple_list1
    |  simple_list1 '||' newline_list simple_list1
    |  simple_list1 '&' simple_list1
    |  simple_list1 ';' simple_list1
    |  pipeline_command
;
pipeline_command= pipeline
    |  '!' pipeline
    |  timespec pipeline
    |  timespec '!' pipeline
    |  '!' timespec pipeline
;
pipeline=command
    | pipeline '|' newline_list pipeline
;
time_opt= '-p';
timespec=  'time'
    | 'time' time_opt;
"""

# """
# 1) generates parser-code from the grammar in this file
# 2) prune the generated source-code text:
#      we only want the source for the parsers
# 3) exec the generated source-code to create the
#      parser-classes / inject them into this namespace
# """
import tatsu

src = tatsu.to_python_sourcecode(GRAMMAR)
src = src[: src.rfind("""def main(filename, **kwargs)""")]
exec(src)
