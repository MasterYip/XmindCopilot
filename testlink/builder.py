#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import json
import logging
import xmind
from io import BytesIO
from datetime import datetime
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, ElementTree, Comment
from xml.sax.saxutils import escape
from testlink import const
from testlink.parser import config, xmind_to_suite


def xmind_to_testlink_json_file(xmind_file):
    """Convert XMind file to a testlink json file"""
    testsuites = get_testlink_testsuites(xmind_file)
    testcases = get_testlink_testcases(testsuites)

    testlink_json_file = xmind_file[:-6] + datetime.now().strftime('-%Y-%m-%d-%H-%M-%S') + '.json'

    with open(testlink_json_file, 'w', encoding='utf8') as f:
        f.write(json.dumps(testcases, indent=4, separators=(',', ': ')))
        logging.info('convert XMind file(%s) to a testlink json file(%s) successfully!', xmind_file, testlink_json_file)

    return testlink_json_file


def xmind_to_testlink_xml_file(xmind_file, is_all_sheet=True):
    """Convert a XMind sheet to a testlink xml file"""
    testsuites = get_testlink_testsuites(xmind_file)
    if not is_all_sheet and testsuites:
        testsuites = [testsuites[0]]

    xml_content = testsuites_to_xml_content(testsuites)
    testsuite_xml_file = xmind_file[:-6] + datetime.now().strftime('-%Y-%m-%d-%H-%M-%S') + '.xml'

    with open(testsuite_xml_file, 'w', encoding='utf-8') as f:
        pretty_content = minidom.parseString(
            xml_content).toprettyxml(indent='\t')
        f.write(pretty_content)
        logging.info('convert XMind file(%s) to a testlink xml file(%s) successfully!', xmind_file, testsuite_xml_file)

    return testsuite_xml_file


def get_testlink_testsuites(xmind_file):
    workbook = xmind.load(xmind_file)
    xmind_content_dict = workbook.getData()
    logging.debug("loading XMind file(%s) dict data: %s", xmind_file, xmind_content_dict)
    if xmind_content_dict:
        testsuites = xmind_to_suite(xmind_content_dict)
        return testsuites
    else:
        logging.error('Invalid XMind file: it is empty!')
        exit(1)  # TODO(devin): look for other best practice!!!


def get_testlink_testcases(testsuites):
    testcases = []

    for testsuite in testsuites:
        product = testsuite.name
        for suite in testsuite.sub_suites:
            for case in suite.testcase_list:
                case_data = case.to_dict()
                case_data['product'] = product
                case_data['suite'] = suite.name
                testcases.append(case_data)

    return testcases


def testsuites_to_xml_content(testsuites):
    root_element = Element(const.TAG_TESTSUITE)

    # setting the root suite's name attribute, that will generate a new testsuite folder on testlink
    # root_element.set(const.ATTR_NMAE, testsuite.name)

    for testsuite in testsuites:
        for sub_suite in testsuite.sub_suites:

            if is_should_skip(sub_suite.name):
                continue

            sub_suite_element = SubElement(root_element, const.TAG_TESTSUITE)
            sub_suite_element.set(const.ATTR_NMAE, sub_suite.name)
            gen_text_element(sub_suite_element, const.TAG_DETAILS, sub_suite.details)
            gen_testcase_element(sub_suite_element, sub_suite)

    testlink = ElementTree(root_element)
    content_stream = BytesIO()
    testlink.write(content_stream, encoding='utf-8', xml_declaration=True)
    return content_stream.getvalue()


def gen_testcase_element(suite_element, suite):
    for testcase in suite.testcase_list:

        if is_should_skip(testcase.name):
            continue

        testcase_elment = SubElement(suite_element, const.TAG_TESTCASE)
        testcase_elment.set(const.ATTR_NMAE, testcase.name)

        gen_text_element(testcase_elment, const.TAG_VERSION, str(testcase.version))
        gen_text_element(testcase_elment, const.TAG_SUMMARY, testcase.summary)
        gen_text_element(testcase_elment, const.TAG_PRECONDITIONS, testcase.preconditions)
        gen_text_element(testcase_elment, const.TAG_EXECUTION_TYPE, _convert_execution_type(testcase.execution_type))
        gen_text_element(testcase_elment, const.TAG_IMPORTANCE, _convert_importance(testcase.importance))

        estimated_exec_duration_element = SubElement(testcase_elment, const.TAG_ESTIMATED_EXEC_DURATION)
        estimated_exec_duration_element.text = str(testcase.estimated_exec_duration)

        status = SubElement(testcase_elment, const.TAG_STATUS)
        status.text = str(testcase.status) if testcase.status in (1, 2, 3, 4, 5, 6, 7) else '7'

        gen_steps_element(testcase_elment, testcase)


def gen_steps_element(testcase_element, testcase):
    if testcase.steps:
        steps_element = SubElement(testcase_element, const.TAG_STEPS)

        for step in testcase.steps:

            if is_should_skip(step.actions):
                continue

            step_element = SubElement(steps_element, const.TAG_STEP)
            gen_text_element(step_element, const.TAG_STEP_NUMBER, str(step.step_number))
            gen_text_element(step_element, const.TAG_ACTIONS, step.actions)
            gen_text_element(step_element, const.TAG_EXPECTEDRESULTS, step.expectedresults)
            gen_text_element(step_element, const.TAG_EXECUTION_TYPE, _convert_execution_type(step.execution_type))


def gen_text_element(parent_element, tag_name, content):
    """generate an element's text conent: <![CDATA[text]]>"""
    if is_should_parse(content):
        child_element = SubElement(parent_element, tag_name)
        element_set_text(child_element, content)


def element_set_text(element, content):
    # retain html tags in content
    content = escape(content, entities={'\r\n': '<br />'})
    # replace new line for *nix system
    content = content.replace('\n', '<br />')
    # add the line break in source to make it readable
    content = content.replace('<br />', '<br />\n')

    # add CDATA for a element  TODO(devin): fix format
    element.append(Comment(' --><![CDATA[' + content.replace(']]>', ']]]]><![CDATA[>') + ']]><!--'))


def is_should_parse(content):
    """An element that has a string content and doesn't start with exclamation mark should be parsing"""
    return isinstance(content, str) and content.strip() != '' and not content[0] in config['ignore_char']


def is_should_skip(content):
    """A testsuite/testcase/teststep should be skip: 1、content is empty; 2、starts with config.ignore_char"""
    return content is None or \
        not isinstance(content, str) or \
        content.strip() == '' or \
        content[0] in config['ignore_char']


def _convert_execution_type(value):
    if value in (1, '手动', '手工', 'manual', 'Manual'):
        return '1'
    elif value in (2, '自动', '自动化', '自动的', 'Automate', 'Automated', 'Automation', 'automate', 'automated', 'automation'):
        return '2'
    else:
        return '1'


def _convert_importance(value):
    mapping = {1: '3', 2: '2', 3: '1'}
    if value in mapping.keys():
        return mapping[value]
    else:
        return '2'