'''
   Based on Parsedom for XBMC plugins
   Copyright (C) 2010-2011 Tobias Ussing And Henrik Mosgaard Jensen

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import re
import log_utils

def _getDOMContent(html, name, match, ret):
    end_str = "</%s" % (name)
    start_str = '<%s' % (name)

    start = html.find(match)
    end = html.find(end_str, start)
    pos = html.find(start_str, start + 1)

    while pos < end and pos != -1:  # Ignore too early </endstr> return
        tend = html.find(end_str, end + len(end_str))
        if tend != -1:
            end = tend
        pos = html.find(start_str, pos + 1)

    if start == -1 and end == -1:
        result = ''
    elif start > -1 and end > -1:
        result = html[start + len(match):end]
    elif end > -1:
        result = html[:end]
    elif start > -1:
        result = html[start + len(match):]
    else:
        result = ''

    if ret:
        endstr = html[end:html.find(">", html.find(end_str)) + 1]
        result = match + result + endstr

    return result

def _getDOMAttributes(match, name, ret):
    pattern = '''<%s [^>]*%s\s*=\s*(?:(['"])(.*?)\\1|([^'"].*?)(?:>|\s))''' % (name, ret)
    results = re.findall(pattern, match, re.I | re.M | re.S)
    return [result[1] if result[1] else result[2] for result in results]

def _getDOMElements(item, name, attrs):
    if not attrs:
        pattern = '(<%s(?: [^>]*>|/?>))' % (name)
        this_list = re.findall(pattern, item, re.M | re.S | re.I)
    else:
        last_list = None
        for key in attrs:
            pattern = '''(<%s [^>]*%s=['"]%s['"][^>]*>)''' % (name, key, attrs[key])
            this_list = re.findall(pattern, item, re.M | re. S | re.I)
            if not this_list and ' ' not in attrs[key]:
                pattern = '''(<%s [^>]*%s=%s[^>]*>)''' % (name, key, attrs[key])
                this_list = re.findall(pattern, item, re.M | re. S | re.I)
    
            if last_list is None:
                last_list = this_list
            else:
                last_list = [item for item in this_list if item in last_list]
        this_list = last_list
    
    return this_list

def parse_dom(html, name='', attrs=None, ret=False):
    if attrs is None: attrs = {}
    log_utils.log('parse_dom: Name: |%s| Attrs: |%s| Ret: |%s| - HTML: %s' % (name, attrs, ret, type(html)), log_utils.LOGDEBUG)
    if isinstance(html, str):
        try:
            html = [html.decode("utf-8")]  # Replace with chardet thingy
        except:
            log_utils.log("Couldn't decode html binary string. Data length: " + repr(len(html)), log_utils.LOGWARNING)
            try:
                html = [html.decode("utf-8", "replace")]
            except:
                log_utils.log("Couldn't decode html binary string (replace). Data length: " + repr(len(html)), log_utils.LOGWARNING)
                html = [html]
    elif isinstance(html, unicode):
        html = [html]
    elif not isinstance(html, list):
        log_utils.log("Input isn't list or string/unicode.", log_utils.LOGWARNING)
        return ''

    if not name.strip():
        log_utils.log("Missing tag name", log_utils.LOGWARNING)
        return ''
    
    if not isinstance(attrs, dict):
        log_utils.log("Attrs must be dictionary", log_utils.LOGWARNING)
        return ''

    ret_lst = []
    for item in html:
        for match in re.findall('(<[^>]*\n[^>]*>)', item):
            item = item.replace(match, match.replace('\n', ' ').replace('\r', ' '))

        lst = _getDOMElements(item, name, attrs)

        if isinstance(ret, str):
            lst2 = []
            for match in lst:
                lst2 += _getDOMAttributes(match, name, ret)
            lst = lst2
        else:
            lst2 = []
            for match in lst:
                temp = _getDOMContent(item, name, match, ret).strip()
                item = item[item.find(temp, item.find(match)):]
                lst2.append(temp)
            lst = lst2
        ret_lst += lst

    # log_utils.log("Done: " + repr(ret_lst), xbmc.LOGDEBUG)
    return ret_lst
