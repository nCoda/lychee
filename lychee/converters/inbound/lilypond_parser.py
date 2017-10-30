#!/usr/bin/env python
# -*- coding: utf-8 -*-

# CAVEAT UTILITOR
#
# This file was automatically generated by TatSu.
#
#    https://pypi.python.org/pypi/tatsu/
#
# Any changes you make to it will be overwritten the next time
# the file is generated.


from __future__ import print_function, division, absolute_import, unicode_literals

from tatsu.buffering import Buffer
from tatsu.parsing import Parser
from tatsu.parsing import tatsumasu
from tatsu.util import re, generic_main  # noqa


KEYWORDS = {
    'R',
    'q',
    'r',
    's',
}  # type: ignore


class LilyPondBuffer(Buffer):
    def __init__(
        self,
        text,
        whitespace=None,
        nameguard=None,
        comments_re='\\%\\{.*?\\%\\}',
        eol_comments_re='%(|[^{].*?)$',
        ignorecase=None,
        namechars='',
        **kwargs
    ):
        super(LilyPondBuffer, self).__init__(
            text,
            whitespace=whitespace,
            nameguard=nameguard,
            comments_re=comments_re,
            eol_comments_re=eol_comments_re,
            ignorecase=ignorecase,
            namechars=namechars,
            **kwargs
        )


class LilyPondParser(Parser):
    def __init__(
        self,
        whitespace=None,
        nameguard=None,
        comments_re='\\%\\{.*?\\%\\}',
        eol_comments_re='%(|[^{].*?)$',
        ignorecase=None,
        left_recursion=False,
        parseinfo=False,
        keywords=None,
        namechars='',
        buffer_class=LilyPondBuffer,
        **kwargs
    ):
        if keywords is None:
            keywords = KEYWORDS
        super(LilyPondParser, self).__init__(
            whitespace=whitespace,
            nameguard=nameguard,
            comments_re=comments_re,
            eol_comments_re=eol_comments_re,
            ignorecase=ignorecase,
            left_recursion=left_recursion,
            parseinfo=parseinfo,
            keywords=keywords,
            namechars=namechars,
            buffer_class=buffer_class,
            **kwargs
        )

    @tatsumasu()
    def _start_(self):  # noqa

        def block0():
            self._top_level_expression_()
        self._closure(block0)
        self._check_eof()

    @tatsumasu()
    def _version_statement_(self):  # noqa
        self._constant('version')
        self.name_last_node('ly_type')
        self._token('\\version')
        self._token('"')

        def sep2():
            self._token('.')

        def block2():
            self._pattern(r'[0-9]*')
        self._gather(block2, sep2)
        self.name_last_node('version')
        self._token('"')
        self.ast._define(
            ['ly_type', 'version'],
            []
        )

    @tatsumasu()
    def _language_statement_(self):  # noqa
        self._constant('language')
        self.name_last_node('ly_type')
        self._token('\\language')
        self._token('"')
        self._pattern(r'[^"]*')
        self.name_last_node('language')
        self._token('"')
        self.ast._define(
            ['language', 'ly_type'],
            []
        )

    @tatsumasu()
    def _instr_name_(self):  # noqa
        self._constant('instr_name')
        self.name_last_node('ly_type')
        self._token('\\set')
        self._token('Staff.instrumentName')
        self._cut()
        self._token('=')
        self._token('"')
        self._pattern(r'[A-Z a-z0-9&]*')
        self.name_last_node('name')
        self._token('"')
        self.ast._define(
            ['ly_type', 'name'],
            []
        )

    @tatsumasu()
    def _clef_(self):  # noqa
        self._constant('clef')
        self.name_last_node('ly_type')
        self._token('\\clef')
        self._cut()
        self._token('"')
        with self._group():
            with self._choice():
                with self._option():
                    self._token('bass')
                with self._option():
                    self._token('tenor')
                with self._option():
                    self._token('alto')
                with self._option():
                    self._token('treble')
                self._error('no available options')
        self.name_last_node('type')
        self._token('"')
        self.ast._define(
            ['ly_type', 'type'],
            []
        )

    @tatsumasu()
    def _key_(self):  # noqa
        self._constant('key')
        self.name_last_node('ly_type')
        self._token('\\key')
        self._cut()
        self._pitch_name_()
        self.name_last_node('keynote')
        self._token('\\')
        with self._group():
            with self._choice():
                with self._option():
                    self._token('major')
                with self._option():
                    self._token('minor')
                self._error('no available options')
        self.name_last_node('mode')
        self.ast._define(
            ['keynote', 'ly_type', 'mode'],
            []
        )

    @tatsumasu()
    def _time_numerator_(self):  # noqa
        self._pattern(r'[1-9][0-9]?')

    @tatsumasu()
    def _time_(self):  # noqa
        self._constant('time')
        self.name_last_node('ly_type')
        self._token('\\time')
        self._cut()
        self._time_numerator_()
        self.name_last_node('count')
        self._token('/')
        self._duration_number_()
        self.name_last_node('unit')
        self.ast._define(
            ['count', 'ly_type', 'unit'],
            []
        )

    @tatsumasu()
    def _staff_setting_(self):  # noqa
        with self._choice():
            with self._option():
                self._clef_()
            with self._option():
                self._key_()
            with self._option():
                self._time_()
            with self._option():
                self._instr_name_()
            self._error('no available options')

    @tatsumasu()
    def _pitch_name_(self):  # noqa
        self._pattern(r'[a-z]+')
        self._check_name()

    @tatsumasu()
    def _octave_(self):  # noqa
        with self._choice():
            with self._option():
                self._token(',,')
            with self._option():
                self._token(',')
            with self._option():
                self._token("'''''")
            with self._option():
                self._token("''''")
            with self._option():
                self._token("'''")
            with self._option():
                self._token("''")
            with self._option():
                self._token("'")
            self._error('no available options')

    @tatsumasu()
    def _accidental_force_(self):  # noqa
        with self._choice():
            with self._option():
                self._token('?')
            with self._option():
                self._token('!')
            self._error('no available options')

    @tatsumasu()
    def _duration_number_(self):  # noqa
        with self._choice():
            with self._option():
                self._token('512')
            with self._option():
                self._token('256')
            with self._option():
                self._token('128')
            with self._option():
                self._token('64')
            with self._option():
                self._token('32')
            with self._option():
                self._token('16')
            with self._option():
                self._token('8')
            with self._option():
                self._token('4')
            with self._option():
                self._token('2')
            with self._option():
                self._token('1')
            self._error('no available options')

    @tatsumasu()
    def _duration_dots_(self):  # noqa

        def block0():
            self._token('.')
        self._closure(block0)

    @tatsumasu()
    def _duration_(self):  # noqa
        with self._choice():
            with self._option():
                with self._group():
                    self._duration_number_()
                    self.name_last_node('dur')
                    self._duration_dots_()
                    self.name_last_node('dots')
            with self._option():
                with self._group():
                    self._void()
                    self.name_last_node('dur')
                    self._empty_closure()
                    self.name_last_node('dots')
            self._error('no available options')
        self.ast._define(
            ['dots', 'dur'],
            []
        )

    @tatsumasu()
    def _tie_(self):  # noqa
        self._constant('tie')
        self.name_last_node('ly_type')
        self._token('~')
        self.ast._define(
            ['ly_type'],
            []
        )

    @tatsumasu()
    def _slur_(self):  # noqa
        self._constant('slur')
        self.name_last_node('ly_type')
        with self._group():
            with self._choice():
                with self._option():
                    self._token('(')
                with self._option():
                    self._token(')')
                self._error('no available options')
        self.name_last_node('slur')
        self.ast._define(
            ['ly_type', 'slur'],
            []
        )

    @tatsumasu()
    def _post_event_(self):  # noqa
        with self._choice():
            with self._option():
                self._tie_()
            with self._option():
                self._slur_()
            self._error('no available options')

    @tatsumasu()
    def _notehead_(self):  # noqa
        self._pitch_name_()
        self.name_last_node('pitch_name')
        self._cut()
        with self._optional():
            self._octave_()
            self.name_last_node('oct')
        with self._optional():
            self._accidental_force_()
            self.name_last_node('accid_force')
        self.ast._define(
            ['accid_force', 'oct', 'pitch_name'],
            []
        )

    @tatsumasu()
    def _note_(self):  # noqa
        self._constant('note')
        self.name_last_node('ly_type')
        self._pitch_name_()
        self.name_last_node('pitch_name')
        self._cut()
        with self._optional():
            self._octave_()
            self.name_last_node('oct')
        with self._optional():
            self._accidental_force_()
            self.name_last_node('accid_force')

        with self._choice():
            with self._option():
                with self._group():
                    self._duration_number_()
                    self.name_last_node('dur')
                    self._duration_dots_()
                    self.name_last_node('dots')
            with self._option():
                with self._group():
                    self._void()
                    self.name_last_node('dur')
                    self._empty_closure()
                    self.name_last_node('dots')
            self._error('no available options')


        def block10():
            self._post_event_()
        self._closure(block10)
        self.name_last_node('post_events')
        self.ast._define(
            ['accid_force', 'dots', 'dur', 'ly_type', 'oct', 'pitch_name', 'post_events'],
            []
        )

    @tatsumasu()
    def _chord_note_(self):  # noqa
        self._constant('note')
        self.name_last_node('ly_type')
        self._pitch_name_()
        self.name_last_node('pitch_name')
        self._cut()
        with self._optional():
            self._octave_()
            self.name_last_node('oct')
        with self._optional():
            self._accidental_force_()
            self.name_last_node('accid_force')


        def block5():
            self._post_event_()
        self._closure(block5)
        self.name_last_node('post_events')
        self.ast._define(
            ['accid_force', 'ly_type', 'oct', 'pitch_name', 'post_events'],
            []
        )

    @tatsumasu()
    def _chord_(self):  # noqa
        self._constant('chord')
        self.name_last_node('ly_type')
        self._token('<')
        with self._ifnot():
            self._token('<')

        def block2():
            self._chord_note_()
        self._closure(block2)
        self.name_last_node('notes')
        self._token('>')
        with self._choice():
            with self._option():
                with self._group():
                    self._duration_number_()
                    self.name_last_node('dur')
                    self._duration_dots_()
                    self.name_last_node('dots')
            with self._option():
                with self._group():
                    self._void()
                    self.name_last_node('dur')
                    self._empty_closure()
                    self.name_last_node('dots')
            self._error('no available options')


        def block9():
            self._post_event_()
        self._closure(block9)
        self.name_last_node('post_events')
        self.ast._define(
            ['dots', 'dur', 'ly_type', 'notes', 'post_events'],
            []
        )

    @tatsumasu()
    def _rest_(self):  # noqa
        self._constant('rest')
        self.name_last_node('ly_type')
        self._pattern(r'r')
        with self._choice():
            with self._option():
                with self._group():
                    self._duration_number_()
                    self.name_last_node('dur')
                    self._duration_dots_()
                    self.name_last_node('dots')
            with self._option():
                with self._group():
                    self._void()
                    self.name_last_node('dur')
                    self._empty_closure()
                    self.name_last_node('dots')
            self._error('no available options')


        def block7():
            self._post_event_()
        self._closure(block7)
        self.name_last_node('post_events')
        self.ast._define(
            ['dots', 'dur', 'ly_type', 'post_events'],
            []
        )

    @tatsumasu()
    def _measure_rest_(self):  # noqa
        self._constant('measure_rest')
        self.name_last_node('ly_type')
        self._pattern(r'R')
        with self._choice():
            with self._option():
                with self._group():
                    self._duration_number_()
                    self.name_last_node('dur')
                    self._duration_dots_()
                    self.name_last_node('dots')
            with self._option():
                with self._group():
                    self._void()
                    self.name_last_node('dur')
                    self._empty_closure()
                    self.name_last_node('dots')
            self._error('no available options')


        def block7():
            self._post_event_()
        self._closure(block7)
        self.name_last_node('post_events')
        self.ast._define(
            ['dots', 'dur', 'ly_type', 'post_events'],
            []
        )

    @tatsumasu()
    def _spacer_(self):  # noqa
        self._constant('spacer')
        self.name_last_node('ly_type')
        self._pattern(r's')
        with self._choice():
            with self._option():
                with self._group():
                    self._duration_number_()
                    self.name_last_node('dur')
                    self._duration_dots_()
                    self.name_last_node('dots')
            with self._option():
                with self._group():
                    self._void()
                    self.name_last_node('dur')
                    self._empty_closure()
                    self.name_last_node('dots')
            self._error('no available options')


        def block7():
            self._post_event_()
        self._closure(block7)
        self.name_last_node('post_events')
        self.ast._define(
            ['dots', 'dur', 'ly_type', 'post_events'],
            []
        )

    @tatsumasu()
    def _barcheck_(self):  # noqa
        self._constant('barcheck')
        self.name_last_node('ly_type')
        self._token('|')
        self.ast._define(
            ['ly_type'],
            []
        )

    @tatsumasu()
    def _music_node_(self):  # noqa
        with self._choice():
            with self._option():
                self._note_()
            with self._option():
                self._rest_()
            with self._option():
                self._spacer_()
            with self._option():
                self._measure_rest_()
            with self._option():
                self._chord_()
            with self._option():
                self._barcheck_()
            self._error('no available options')

    @tatsumasu()
    def _nodes_(self):  # noqa

        def block0():
            with self._choice():
                with self._option():
                    with self._choice():
                        with self._option():
                            self._note_()
                        with self._option():
                            self._rest_()
                        with self._option():
                            self._spacer_()
                        with self._option():
                            self._measure_rest_()
                        with self._option():
                            self._chord_()
                        with self._option():
                            self._barcheck_()
                        self._error('no available options')
                with self._option():
                    with self._choice():
                        with self._option():
                            self._clef_()
                        with self._option():
                            self._key_()
                        with self._option():
                            self._time_()
                        with self._option():
                            self._instr_name_()
                        self._error('no available options')
                self._error('no available options')
        self._positive_closure(block0)

    @tatsumasu()
    def _unmarked_layer_(self):  # noqa
        self._nodes_()

    @tatsumasu()
    def _marked_layer_(self):  # noqa
        self._token('{')
        self._nodes_()
        self.name_last_node('@')
        self._token('}')

    @tatsumasu()
    def _monophonic_layers_(self):  # noqa
        self._unmarked_layer_()
        self.add_last_node_to_name('layers')
        self.ast._define(
            [],
            ['layers']
        )

    @tatsumasu()
    def _polyphonic_layers_(self):  # noqa
        self._simul_l_()
        with self._group():

            def sep1():
                self._token('\\\\')

            def block1():
                self._marked_layer_()
            self._gather(block1, sep1)
        self.name_last_node('layers')
        self._simul_r_()
        self.ast._define(
            ['layers'],
            []
        )

    @tatsumasu()
    def _brace_l_(self):  # noqa
        self._token('{')

    @tatsumasu()
    def _brace_r_(self):  # noqa
        self._token('}')

    @tatsumasu()
    def _staff_content_(self):  # noqa

        def block1():
            self._staff_setting_()
        self._closure(block1)
        self.name_last_node('initial_settings')

        def block3():
            with self._group():
                with self._choice():
                    with self._option():
                        self._monophonic_layers_()
                    with self._option():
                        self._polyphonic_layers_()
                    self._error('no available options')
        self._positive_closure(block3)
        self.name_last_node('content')
        self.ast._define(
            ['content', 'initial_settings'],
            []
        )

    @tatsumasu()
    def _token_new_(self):  # noqa
        self._token('\\new')

    @tatsumasu()
    def _token_staff_(self):  # noqa
        self._token('Staff')

    @tatsumasu()
    def _staff_(self):  # noqa
        self._constant('staff')
        self.name_last_node('ly_type')
        self._token_new_()
        self._token_staff_()
        self._brace_l_()

        def block2():
            self._staff_setting_()
        self._closure(block2)
        self.name_last_node('initial_settings')

        def block4():
            with self._group():
                with self._choice():
                    with self._option():
                        self._monophonic_layers_()
                    with self._option():
                        self._polyphonic_layers_()
                    self._error('no available options')
        self._positive_closure(block4)
        self.name_last_node('content')

        self._brace_r_()
        self.ast._define(
            ['content', 'initial_settings', 'ly_type'],
            []
        )

    @tatsumasu()
    def _simul_l_(self):  # noqa
        self._token('<<')

    @tatsumasu()
    def _simul_r_(self):  # noqa
        self._token('>>')

    @tatsumasu()
    def _score_staff_content_(self):  # noqa
        with self._choice():
            with self._option():
                self._simul_l_()
                self._cut()

                def block1():
                    self._staff_()
                self._positive_closure(block1)
                self.name_last_node('@')
                self._simul_r_()
            with self._option():
                self._staff_()
                self.name_last_node('@')
            self._error('no available options')

    @tatsumasu()
    def _header_block_(self):  # noqa
        self._token('\\header')
        self._brace_l_()
        self._brace_r_()

    @tatsumasu()
    def _layout_block_(self):  # noqa
        self._token('\\layout')
        self._brace_l_()
        self._brace_r_()

    @tatsumasu()
    def _paper_block_(self):  # noqa
        self._token('\\paper')
        self._brace_l_()
        self._brace_r_()

    @tatsumasu()
    def _token_score_(self):  # noqa
        with self._choice():
            with self._option():
                self._token('\\score')
            with self._option():
                self._token('\\new')
                self._token('Score')
            self._error('no available options')

    @tatsumasu()
    def _score_(self):  # noqa
        self._constant('score')
        self.name_last_node('ly_type')
        with self._optional():
            self._version_statement_()
        self.name_last_node('version')
        self._token_score_()
        with self._group():
            with self._choice():
                with self._option():
                    self._score_staff_content_()
                    self.name_last_node('staves')
                with self._option():
                    self._brace_l_()
                    self._score_staff_content_()
                    self.name_last_node('staves')
                    with self._optional():
                        self._layout_block_()
                        self.name_last_node('layout_block')
                    self._brace_r_()
                with self._option():
                    self._brace_l_()
                    self._token_score_()
                    self._score_staff_content_()
                    self.name_last_node('staves')
                    self._brace_r_()
                self._error('no available options')
        self.ast._define(
            ['layout_block', 'ly_type', 'staves', 'version'],
            []
        )

    @tatsumasu()
    def _top_level_expression_(self):  # noqa
        with self._choice():
            with self._option():
                self._version_statement_()
            with self._option():
                self._language_statement_()
            with self._option():
                self._header_block_()
            with self._option():
                self._layout_block_()
            with self._option():
                self._paper_block_()
            with self._option():
                self._score_()
            with self._option():
                self._staff_()
            self._error('no available options')


class LilyPondSemantics(object):
    def start(self, ast):  # noqa
        return ast

    def version_statement(self, ast):  # noqa
        return ast

    def language_statement(self, ast):  # noqa
        return ast

    def instr_name(self, ast):  # noqa
        return ast

    def clef(self, ast):  # noqa
        return ast

    def key(self, ast):  # noqa
        return ast

    def time_numerator(self, ast):  # noqa
        return ast

    def time(self, ast):  # noqa
        return ast

    def staff_setting(self, ast):  # noqa
        return ast

    def pitch_name(self, ast):  # noqa
        return ast

    def octave(self, ast):  # noqa
        return ast

    def accidental_force(self, ast):  # noqa
        return ast

    def duration_number(self, ast):  # noqa
        return ast

    def duration_dots(self, ast):  # noqa
        return ast

    def duration(self, ast):  # noqa
        return ast

    def tie(self, ast):  # noqa
        return ast

    def slur(self, ast):  # noqa
        return ast

    def post_event(self, ast):  # noqa
        return ast

    def notehead(self, ast):  # noqa
        return ast

    def note(self, ast):  # noqa
        return ast

    def chord_note(self, ast):  # noqa
        return ast

    def chord(self, ast):  # noqa
        return ast

    def rest(self, ast):  # noqa
        return ast

    def measure_rest(self, ast):  # noqa
        return ast

    def spacer(self, ast):  # noqa
        return ast

    def barcheck(self, ast):  # noqa
        return ast

    def music_node(self, ast):  # noqa
        return ast

    def nodes(self, ast):  # noqa
        return ast

    def unmarked_layer(self, ast):  # noqa
        return ast

    def marked_layer(self, ast):  # noqa
        return ast

    def monophonic_layers(self, ast):  # noqa
        return ast

    def polyphonic_layers(self, ast):  # noqa
        return ast

    def brace_l(self, ast):  # noqa
        return ast

    def brace_r(self, ast):  # noqa
        return ast

    def staff_content(self, ast):  # noqa
        return ast

    def token_new(self, ast):  # noqa
        return ast

    def token_staff(self, ast):  # noqa
        return ast

    def staff(self, ast):  # noqa
        return ast

    def simul_l(self, ast):  # noqa
        return ast

    def simul_r(self, ast):  # noqa
        return ast

    def score_staff_content(self, ast):  # noqa
        return ast

    def header_block(self, ast):  # noqa
        return ast

    def layout_block(self, ast):  # noqa
        return ast

    def paper_block(self, ast):  # noqa
        return ast

    def token_score(self, ast):  # noqa
        return ast

    def score(self, ast):  # noqa
        return ast

    def top_level_expression(self, ast):  # noqa
        return ast


def main(filename, startrule, **kwargs):
    with open(filename) as f:
        text = f.read()
    parser = LilyPondParser()
    return parser.parse(text, startrule, filename=filename, **kwargs)


if __name__ == '__main__':
    import json
    from tatsu.util import asjson

    ast = generic_main(main, LilyPondParser, name='LilyPond')
    print('AST:')
    print(ast)
    print()
    print('JSON:')
    print(json.dumps(asjson(ast), indent=2))
    print()
