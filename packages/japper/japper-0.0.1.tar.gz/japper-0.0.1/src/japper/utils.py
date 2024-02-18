import os
from IPython.display import display, HTML, Javascript
import base64
import hashlib

js_output = None


class ExternalFuncs:
    show_loading = None
    hide_loading = None
    toast_alert = None


_nav_menu = None


def get_nav_menu():
    return _nav_menu


def set_nav_menu(value):
    global _nav_menu
    _nav_menu = value


def set_message_funcs(show_loading_func, hide_loading_func, toast_alert_func):
    """
    The actual components and methods are implemented in the AppMainView class
    The connection is performed in the AppMainController class
    """
    ExternalFuncs.show_loading = show_loading_func
    ExternalFuncs.hide_loading = hide_loading_func
    ExternalFuncs.toast_alert = toast_alert_func


def show_loading(msg='Loading...'):
    """
    Show loading dialog
    """
    if ExternalFuncs.show_loading is not None:
        ExternalFuncs.show_loading(msg)


def hide_loading():
    """
    Hide loading dialog
    """
    if ExternalFuncs.hide_loading is not None:
        ExternalFuncs.hide_loading()


def toast_alert(msg, type='info'):
    """
    Show alert
    """
    if ExternalFuncs.toast_alert is not None:
        ExternalFuncs.toast_alert(msg, type)


def set_js_output(output):
    global js_output
    js_output = output


def run_js(js):
    """
    Run JS code using the dedicated output widget
    This is a hack to fix the issue of the blank space at the bottom of the page when new JS is executed.
    @param js:
    @return:
    """
    display(Javascript(js))  # voila now can handle this issue
    # if js_output is not None:
    #     js_output.append_display_data(Javascript(js))
    #     js_output.clear_output()
    # else:
    #     display(Javascript(js))


def run_js_with_wait(js, selector):
    """
    Run JS code with a wait for a selector
    :param js:
    :param selector:
    :return:
    """
    run_js("""
        function waitForElement(selector, callBack){
          window.setTimeout(function(){
            var element = document.querySelector(selector);
            if(element){
              callBack(selector, element);
            }else{
              waitForElement(selector, callBack);
            }
          },500)
        }

        waitForElement('%s',function(selector, element){
            %s
        });
    """ % (selector, js))


def download_csv_data(contents, filename):
    """
    Download csv data as a file
    """
    if type(contents) == str:
        contents = bytes(contents, 'utf-8')

    b64 = base64.b64encode(contents)
    payload = b64.decode()
    digest = hashlib.md5(contents).hexdigest()  # bypass browser cache
    id = f'dl_{digest}'

    with js_output:
        display(
            HTML(f"""
        <html>
        <body>
        <a id="{id}" download="{filename}.csv" href="data:text/csv;base64,{payload}"></a>

        <script>
        (function download() {{
        document.getElementById('{id}').click();
        }})()
        </script>

        </body>
        </html>
        """))

    js_output.clear_output()


def download_file(filepath):
    with js_output:
        display(
            HTML(f"""
            <a id="tmp_download" download="{os.path.basename(filepath)}" href="{filepath}"></a>
            <script>
                (function download() {{
                    let elem = document.getElementById('tmp_download');
                    elem.click();
                    elem.remove();
                }})();
            </script>
        """))

    js_output.clear_output()


def inject_html(filepath):
    base_dir = os.path.dirname(__file__)
    display(HTML(filename=base_dir + '/' + filepath))


def inject_css(filepath):
    base_dir = os.path.dirname(__file__)
    with open(base_dir + '/' + filepath, 'r') as f:
        css = f.read()
        display(HTML(f"""
            <style>
                {css}
            </style>
        """))
