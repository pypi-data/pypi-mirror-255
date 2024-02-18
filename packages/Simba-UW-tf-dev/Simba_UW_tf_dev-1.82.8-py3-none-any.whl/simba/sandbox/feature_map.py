from simba.mixins.statistics_mixin import Statistics
import inspect
from copy import deepcopy
import itertools, re


FEATURE_FILES = [Statistics]



for feature_extrator_file in FEATURE_FILES:
    cls_instance = feature_extrator_file
    meth_info = {}
    for method_name, method in cls_instance.__dict__.items():
        if callable(method) and not method_name.startswith("__"):
            doc_str, type_hints = method.__doc__, inspect.signature(method)
        elif isinstance(method, staticmethod):
            doc_str, type_hints = method.__func__.__doc__, inspect.signature(method.__func__)
        else:
            continue
        meth_info[method_name] = {'doc_str': doc_str, 'type_hints': type_hints}

    meth_info_cpy = deepcopy(meth_info)
    for method_name, method_data in meth_info.items():
        input, output = str(method_data['type_hints']).split('->')[0], str(method_data['type_hints']).split('->')[-1].strip()
        input = input.replace('(', '').replace(')', '').strip().split(',')
        meth_args = {}
        for arg in input:
            try:
                arg_name, arg_dtype = arg.split(':')[0].strip(), arg.split(':')[1].strip()
                meth_args[arg_name] = arg_dtype
            except:
                pass
        meth_info_cpy['output'] = output
        meth_info_cpy['input'] = meth_args

    for method_name, method_data in meth_info.items():
        try:
            if method_data['doc_str']:
                doc_str = method_data['doc_str'].split('\n')
                doc_str_comps, componenets = [], []
                for cnt, i in enumerate(doc_str):
                    if i == '':
                        doc_str_comps.append(componenets)
                        componenets = []
                    else:
                        componenets.append(i.strip())
                doc_str_comps = [x for x in doc_str_comps if x != []]
                meth_info_cpy['summary'] = doc_str_comps[0][0]
                for item in itertools.chain.from_iterable(doc_str_comps):
                    if item.startswith('.. image:'):
                        meth_info_cpy['img_path'] = item.split('::')[-1].strip()

                    if item.startswith('.. math:'):
                        meth_info_cpy['equation'] = item.split('::')[-1].strip()


        except:
            pass


        #signature = inspect.signature(str(method_data['type_hints']))





