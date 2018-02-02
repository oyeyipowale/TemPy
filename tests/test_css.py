# -*- coding: utf-8 -*-
"""
@author: Federico Cerchiari <federicocerchiari@gmail.com>
"""
import os
import unittest
from copy import copy
from collections import Counter

from tempy import Css
from tempy.tags import A, Div
from tempy.exceptions import WrongContentError, AttrNotFoundError, WrongArgsError


class TestTag(unittest.TestCase):

    def setUp(self):
        self.css_dict = {
            'html': {
                'background-color': 'lightblue'
                },
            'h1': {
                'color': 'white',
                'text-align': 'center'
                }
            }

    def test_init(self):
        # Test init from dict
        css = Css(self.css_dict)
        self.assertTrue(all(item in css.attrs['css_attrs'].items() for item in self.css_dict.items()))

        # Test init unpacked dict
        css = Css(**self.css_dict)
        self.assertTrue(all(item in css.attrs['css_attrs'].items() for item in self.css_dict.items()))

        # Test init list of dicts
        css_dict2 = {'div': {'color': 'blue'}}
        compare_dict = copy(self.css_dict)
        compare_dict.update(css_dict2)
        css = Css([self.css_dict, css_dict2])
        self.assertTrue(all(item in css.attrs['css_attrs'].items() for item in compare_dict.items()))

        # Test init generator of dicts
        css_dict2 = {'div': {'color': 'blue'}}
        compare_dict = copy(self.css_dict)
        compare_dict.update(css_dict2)
        css = Css((self.css_dict, css_dict2))
        self.assertTrue(all(item in css.attrs['css_attrs'].items() for item in compare_dict.items()))

        with self.assertRaises(WrongContentError):
            Css('test', 'wrong')

        with self.assertRaises(WrongContentError):
            Css(['test', 'wrong'])

    def test_update(self):
        add_dict = {'div': {'color': 'blue'}}
        modify_dict = {'html': {'background-color': 'black'}}

        add_compare_dict = copy(self.css_dict)
        add_compare_dict.update(add_dict)

        modify_compare_dict = copy(self.css_dict)
        modify_compare_dict.update(modify_dict)

        # Test add from dict
        css = Css(self.css_dict)
        css.update(add_dict)
        self.assertTrue(all(item in css.attrs['css_attrs'].items() for item in add_compare_dict.items()))

        # Test modify from dict
        css = Css(self.css_dict)
        css.update(modify_dict)
        self.assertTrue(all(item in css.attrs['css_attrs'].items() for item in modify_compare_dict.items()))

        # Test add from unpacked dict
        css = Css(self.css_dict)
        css.update(**add_dict)
        self.assertTrue(all(item in css.attrs['css_attrs'].items() for item in add_compare_dict.items()))

        # Test modify from unpacked dict
        css = Css(self.css_dict)
        css.update(**modify_dict)
        self.assertTrue(all(item in css.attrs['css_attrs'].items() for item in modify_compare_dict.items()))

        with self.assertRaises(WrongContentError):
            css = Css(self.css_dict)
            css.update('test', 'wrong')

        with self.assertRaises(WrongContentError):
            css = Css(self.css_dict)
            css.update(['test', 'wrong'])

    def test_function_content(self):
        css = Css({'h1': {'color': lambda: 'TEST'}})
        self.assertTrue('TEST' in css.render())

    def test_render(self):
        css = Css(self.css_dict)
        rendered_css = css.render()
        expected_counter = Counter('<style>html { background-color: lightblue; } h1 { color: white; text-align: center; } </style>')
        expected_counter['{'] += 1
        expected_counter['}'] += 1
        expected_counter[' '] += 2
        # We count chars occurrence 'cause in python < 3.6 kwargs is not an OrderedDict'
        self.assertEqual(Counter(rendered_css), expected_counter)

    def test_dump(self):
        css = Css({'div': {'color': 'blue'}})
        expected = '{ } div { color: blue; } '
        filename = 'temp.css'
        css.dump(filename)
        with open(filename, 'r') as f:
            self.assertEqual(f.read(), expected)
        os.remove(filename)

    def test_replace_element(self):
        link = A()
        css = Css({'html': {
                'body': {
                    'color': 'red',
                    Div: {
                        'color': 'green',
                        'border': '1px'
                    },
                    link: {'color': 'purple'},
                    A: {'color': 'yellow'}
                }
            },
            '#myid': {'color': 'blue'}
        })

        css_values = {'html': {
                'body': {
                    'color': 'red',
                    Div: {
                        'color': 'green',
                        'border': '1px'
                    },
                    link: {'color': 'purple'},
                    A: {'color': 'yellow'}
                }
            },
            '#myid': {'color': 'blue'}
        }

        css.replace_element(['#myid'], {'color': 'purple'})
        self.assertEqual({'color': 'purple'}, css.attrs['css_attrs']['#myid'])

        #nested example
        # css.replace_element(['html', 'body', link], {'color': 'grey'})
        # self.assertEqual({'color': 'grey'}, css.attrs['css_attrs']['html']['body'][link])
        #
        # #failed to find
        # css.replace_element(['myid'], {'color': 'purple'})
        # self.assertEqual({'color': 'purple'}, css.attrs['css_attrs']['#myid'])
        # with self.assertRaises(AttrNotFoundError):
        #     css.replace_element(['myid'], {'color': 'purple'}, ignore_error=False)
        #
        # #wrong args type
        # css.replace_element('', None)
        # self.assertEqual(css_values, css.attrs['css_attrs'])
        # with self.assertRaises(WrongArgsError):
        #     css.replace_element('', None, ignore_error=False)
        #
        # css.replace_element('', {'color': 'purple'})
        # self.assertEqual(css_values, css.attrs['css_attrs'])
        # with self.assertRaises(WrongArgsError):
        #     css.replace_element('', {'color': 'purple'}, ignore_error=False)

