import json
import uuid
import pprint
from treelib import Tree
import pandas as pd
import os
import requests
import io
import zipfile
import urllib3


class Ref_xplainsession:
    __url__ = ""

    __cookies__ = ""

    __xplain_session__ = {}

    __headers__ = ""

    __last_error__ = {}

    __id__ = ""

    __pp__ = pprint.PrettyPrinter(indent=4)

    __broadcast__ = True

    """python client class for calling Xplain Web API

    Example:
        >>> from xplain import XplainSession
        >>> s = XplainSession(url="myhost:8080", user="me", password="secret")

    """

    def __parseResponse__(self, response):
        return json.loads(response.text)

    def _build_dataframe(self, children, dataSet, data_fields):
        for child in children:
            if child.get('children') is not None:
                self._build_dataframe(child['children'], dataSet, data_fields)
            else:
                for field in data_fields:
                    for rec in child['data']:
                        if isinstance(rec[field], str):
                            dataSet[field].append(rec[field])
                        else:
                            if rec[field].get('value') is not None:
                                dataSet[field].append(rec[field]['value'])
                            else:
                                dataSet[field].append(None)

    def convert_to_dataframe(self, data):
        """
        convert result JSON to DataFrame format

        :param data: data in JSON format
        :return: data in pandas data frame format
        """

        if data.get("fields") is not None:
            data_fields = data['fields']
        else:
            data_fields = []

        if data.get("children") is not None:
            children = data["children"]
        else:
            children = []

        dataSet = {}
        for field in data_fields:
            dataSet[field] = []

        self._build_dataframe(children, dataSet, data_fields)
        # for child in children:
        #     for field in data_fields:
        #         for rec in child['data']:
        #             if isinstance(rec[field], str):
        #                 dataSet[field].append(rec[field])
        #             else:
        #                 if rec[field].get('value') != None:
        #                     dataSet[field].append(rec[field]['value'])
        #                 else:
        #                     dataSet[field].append(None)

        df = pd.DataFrame(dataSet)
        return df

    def __buildTree__(self, new_tree, json_object, parent_id):
        object_root = json_object['objectName']
        root_id = uuid.uuid4()
        if parent_id is None:
            new_tree.create_node('(( ' + object_root + ' ))', root_id)
        else:
            new_tree.create_node('(( ' + object_root + ' ))', root_id,
                                 parent=parent_id)

        for dimension in json_object['dimensions']:
            dimension_id = uuid.uuid4()
            new_tree.create_node(dimension['dimensionName'], dimension_id,
                                 parent=root_id)
            if dimension.get('attributes') is not None:
                for attribute in dimension['attributes']:
                    attribute_id = uuid.uuid4()
                    new_tree.create_node(attribute['attributeName'],
                                         attribute_id, parent=dimension_id)
        if json_object.get('childObjects') is not None:
            for childObject in json_object['childObjects']:
                self.__buildTree__(new_tree, childObject, root_id)

        return new_tree

    def get_session_id(self):
        return self.__id__

    def perform(self, payload):
        """
        Send POST request against entry point /xplainsession with payload as
        json

        :param payload: xplain web api in json
        :return: request response as JSON
        """
        payload_dump = json.dumps(payload)
        response = requests.post(self.__url__ + "/xplainsession",
                                 data=payload_dump,
                                 cookies=self.__cookies__,
                                 headers=self.__headers__,
                                 verify=False)
        return self.__parseResponse__(response)

    def _broadcast_update(self):
        '''
        use websocket to broadcast session update
        '''

        payload = json.dumps({"sessionId": self.__id__})
        requests.post(self.__url__ + "/broadcast", data=payload,
                      cookies=self.__cookies__,
                      headers=self.__headers__,
                      verify=False)

    def _store_error_and_show_message(self, response):
        responseJson = self.__parseResponse__(response)
        self.__last_error__ = responseJson
        self.print_error()

    def print_last_stack_trace(self):
        """
        print the stack trace of last error
        """
        if self.__last_error__.get('stacktrace') is not None:
            self.__pp__.pprint(self.__last_error__['stacktrace'])

    def print_error(self):
        """
        print the last error message

        :return:
        """
        if self.__last_error__.get('localized_error_messages') is not None:
            self.__pp__.pprint(self.__last_error__['localized_error_messages'])

    def download_result(self, filename, save_as):
        """

        """
        download_url = self.__url__ + "/downloadfile?filename=" + filename
        response = requests.get(download_url,
                                cookies=self.__cookies__,
                                headers=self.__headers__,
                                verify=False)
        open(save_as, 'wb').write(response.content)

    def upload2data(self, file_name):
        data = open(file_name, 'rb')
        files = {file_name: data}
        payload = {
            "filename": file_name,
            "type": "DATA"
        }
        url = self.__url__ + "/upload2data"
        headers = self.__headers__
        # headers["content-type"] = "multipart/form-data"
        requests.post(url,
                      cookies=self.__cookies__,
                      headers=headers,

                      verify=False,
                      files=files,
                      data=payload
                      )

    def post(self, payload):
        """
        Send POST request against entry point /xplainsession with payload as
        json

        :param payload: xplain web api in json
        :return: request response as JSON
        """
        # payload_dump = json.dumps(payload)

        response = requests.post(self.__url__ + "/xplainsession", data=payload,
                                 cookies=self.__cookies__,
                                 headers=self.__headers__,
                                 verify=False)
        return response

    def post_and_broadcast(self, payload):
        """
        Send POST request against entry point /xplainsession with payload as
        json, and notify
        the backend to update the session which shares the same session id

        :param payload: xplain web api in json

        Example:
            >>> import xplain as x
            >>> x.connect(url="myhost:8080", user="myUser", password="myPwd")
            >>> x.startup("mystartup")
            >>> x.post_and_broadcast({
                        "method": "clearAllSelections"
                     })

        """

        response = self.post(payload)
        if response.status_code == 200:
            response_json = self.__parseResponse__(response)
            self.store_xsession(response_json)
            if self.__broadcast__:
                self._broadcast_update()
        else:
            print("perform xplain method has failed")
            self._store_error_and_show_message(response)
            raise Exception(self.__last_error__)

    def run(self, method):
        """
        perform xplain web api method and broadcast the change to other
        client sharing with same session id

        :param method: xplain web api method in json format
        :type method: json

        Example:
            >>> import xplain as x
            >>> x.connect(url="myhost:8080", user="myUser", password="myPwd")
            >>> x.startup("mystartup")
            >>> x.run({
                        "method": "clearAllSelections"
                     })
        """
        payload = json.dumps(method)
        self.post_and_broadcast(payload)

    def get(self, params=None):
        """

        Send GET request against entry point /xplainsession with URL parameters
        :param params: URL parameters
        :return: response in JSON
        """
        response = requests.get(self.__url__ + '/xplainsession', params=params,
                                cookies=self.__cookies__, verify=False)
        return response

    def store_xsession(self, response_json):
        try:
            if response_json.get('session') is not None:
                self.__xplain_session__ = response_json["session"][0]["element"]
                self.__id__ = self.__xplain_session__['sessionName']
            else:
                if response_json.get('sessionName') is not None:
                    self.__xplain_session__ = response_json
                    self.__id__ = response_json["sessionName"]
        except:
            print("no session json found")

    def _load_session(self, startup_option):
        params = {"startupconfig": startup_option}
        response = self.get(params)
        if (response.status_code == 200):
            method = {"method": "setResultsFormat", "format": "unified"}

            payload = json.dumps(method)
            response = self.post(payload)
            if (response.status_code == 200):
                response_json = self.__parseResponse__(response)
                self.store_xsession(response_json)
                print("xplain session from " + startup_option + " initiated")
            else:
                print("setResultsFormat has failed")
                raise Exception("startup -> setResultsFormat has failed")

        else:
            print("startup has failed")
            raise Exception("startup has failed")

    def get_result(self, query_name, data_frame=True):
        """
        et the result of a certain request id

        :param query_name:  the query name or id
        :param data_frame: if result shall be returned as pandas data frame
        :return: the result of specified query
        :rtype: json
        """

        if self.__xplain_session__.get('requests') is not None:
            for xrequest in self.__xplain_session__["requests"]:
                if xrequest["requestName"] == query_name:
                    if data_frame:
                        return self.convert_to_dataframe(xrequest["results"][0])
                    else:
                        return xrequest["results"][0]

    def open_query(self, query, data_frame=True):
        """
         perform the query and keep it open, the result of this query will be
         impacted by further modification of current session, like selection
         changes

        :param query: either xplain.Query instance or JSON
        :param data_frame: if True, the result will be returned as dataFrame
        :return:  result of given query
        :rtype:  JSON or DataFrame, depending on parameter dataFrame
        """

        if query.__class__.__name__ == "Query":
            query = query.to_json()

        if query.get('requestName') != None:
            request_id = query['requestName']
        else:
            request_id = str(uuid.uuid4())
            query['requestName'] = request_id

        methodCall = {
            'method': 'openRequest',
            'request': query
        }

        self.run(methodCall)
        return self.get_result(request_id, data_frame)

    def terminate(self):
        '''
        Terminate the current xplain session.

        :return:
        '''
        requests.get(self.__url__ + '/logout', cookies=self.__cookies__,
                     headers=self.__headers__, verify=False)
        print("logged out")

    def __init__(self, url='http://localhost:8080', user='user',
                 password='xplainData'):

        urllib3.disable_warnings()
        s = requests.Session()
        s.headers.update({
            # "X-CSRF-TOKEN": "dummy",
            # "X-Requested-With": "XMLHttpRequest",
            # "Origin": url,
            # "Content-Type": "application/json"

        })
        self.__headers__ = s.headers

        self.__url__ = url

        response = s.get(url + "/user", verify=False)
        csrf = response.headers.get("X-CSRF-TOKEN")
        headers = {'User-Agent': 'Mozilla/5.0'}
        payload = {"username": user, "password": password, "_csrf": csrf}
        response = s.post(url=url + "/login", headers=headers,
                          data=payload, verify=False)
        if response.status_code == 200:
            self.__cookies__ = response.cookies
            response = s.get(url + "/user", verify=False)
            csrf = response.headers.get("X-CSRF-TOKEN")
            s.headers.update({"X-CSRF-TOKEN": csrf})
            self.__headers__ = s.headers
            print("Authentication successful!!!")
        else:
            print("authetication failed")

    def startup(self, startup_file):
        """
        load xplain session by given startup configuration file name without
        file extension
        :param startup_file: the file name of startup configuration,
        :type startup_file: string
        """
        if ".xstartup" not in str(startup_file):
            startup_file = str(startup_file) + ".xstartup"
        self._load_session(startup_file)

    def load_from_session_id(self, session_id):
        """
        load xplain session by given exisiting session id

        :param session_id: the 32 digit  xplain session id
        """
        self._load_session(session_id)

    def open_attribute(self, object_name, dimension_name, attribute_name,
                       request_name='',
                       data_frame=True):
        """
        convinient method to open an attribute

        :param object_name: name of object
        :param dimension_name: name of dimension
        :param attribute_name: name of attribute
        :param request_name: id or name of request
        :param data_frame: boolean: if result shall be returned as pandas
        data frame
        :return: attribute groupped by on first level and aggregated by count.
        :rtype: Attribute
        Example:
            >>> import xplain as x
            >>> x.connect(url="myhost:8080", user="myUser", password="myPwd")
            >>> x.startup("mystartup")
            >>> x.open_attribute("Patient", "Age", "Agegroup")
        """

        if request_name == '':
            request_id = str(uuid.uuid4())
            method = {
                "method": "openAttribute",
                "object": object_name,
                "dimension": dimension_name,
                "attribute": attribute_name,
                "requestName": request_id

            }
        else:
            request_id = request_name
            method = {
                "method": "openAttribute",
                "object": object_name,
                "dimension": dimension_name,
                "attribute": attribute_name,
                "requestName": request_id
            }
        succ = self.post(method)
        if (succ):
            return self.get_result(request_id, data_frame)

    def pprint(self, content):
        """
        pretty printing the content
        :param content: the content to be pretty printed
        :return:
        """

        self._pp.pprint(content)

    def execute_query(self, query, data_frame=True):
        """
        execute the xplain request

        :param query: xplain.Query or JSON, specification of the query,
        the data type could be either Query or JSON
        :param data_frame: if True, the result will be returned as dataFrame
        :return:  result of given query
        :rtype:  JSON or DataFrame, depending on parameter dataFrame
        Example:
            >>> # option 1, query config object
            >>>  query_config = xplain.Query_config()
            >>>  query_config.add_aggregation(object_name="AU-Diagnosen",
            >>>  dimension_name="Diagnose", type="COUNT")
            >>>  query_config.add_groupby(object_name="AU-Diagnosen",
            >>> dimension_name="Diagnose", attribute_name="FDB_ICD")
            >>> query_config.add_selection(object_name="AU-Diagnosen",
            >>> dimension_name="Datum_von", attribute_name="AU_von",
                                       selected_states=["2020-12"])
            >>> session.execute_query(query_config)

            >>> # option 2,  query in json
            >>> query = {
            >>>    "aggregations" :[
            >>>        {
            >>>            "object": "AU-Diagnosen",
            >>>            "dimension": "Diagnose",
            >>>            "type": "SUM"
            >>>        }
            >>>    ],
            >>>    "groupBys":[{
            >>>        "attribute": {
            >>>            "object": "AU-Diagnose",
            >>>            "dimension": "Diagnose",
            >>>            "attribute": "FDB_ICD"
            >>>        }
            >>>    }
            >>> }

            >>> session.execute_query(query)
        """

        # if parameter is instance of class Query,
        # then convert it to json
        if query.__class__.__name__ == "Query_config":
            query = query.to_json()

        if query.get('requestName') != None:
            request_id = query['requestName']
        else:
            request_id = str(uuid.uuid4())
            query['requestName'] = request_id

        method_call = {
            'method': 'executeRequest',
            'request': query
        }

        self.run(method_call)
        return self.get_result(request_id, data_frame)

    def show_tree(self):
        """
        show object tree

        :return: render the object hierarchy as a tree
        :rtype: string
        """

        new_tree = Tree()
        tree = self.__buildTree__(new_tree, self.__xplain_session__[
            'focusObject'], parent_id=None)
        tree.show()

    def show_tree_details(self):
        """
        show object tree in details
        """
        self.pprint(self.__xplain_session__['focusObject'])

    def get_session(self):
        return self.__xplain_session__

    def get_selections(self):
        if self.__xplain_session__.get('globalSelections') is not None:
            return self.__xplain_session__['globalSelections']

    def get_object_info(self, object_name, root=None):
        """
        find and display the details of a xobject in json

        :param object_name:
        :param root: the object name from where the search starts. if none
        root is provided, the root node of the entire
        object tree
        :return: details of the Xobject in json
        """
        result = self._get_object_info(object_name)
        if result is not None:
            return result
        else:
            print("XObject " + object_name + " is not found")

    def _get_object_info(self, object_name, root=None):
        if root is None:
            root = self.get_session()['focusObject']
        if root['objectName'] == object_name:
            return root
        else:
            if root.get('childObjects') is not None:
                for obj in root['childObjects']:
                    obj_found = self._get_object_info(object_name, obj)
                    if obj_found is not None:
                        return obj_found
            else:
                return None

    def get_dimension_info(self, object_name, dimension_name):
        """
        find and retrieves the details of a dimension

        :param object_name: the name of the xobject
        :param dimension_name: the name of dimension
        :return: details of this dimension in json format
        """

        object = self.get_object_info(object_name)
        if object is not None:
            for dimension_obj in object['dimensions']:
                if dimension_obj['dimensionName'] == dimension_name:
                    return dimension_obj
            print("XDimension " + dimension_name + " is not found")
            return None

    def get_attribute_info(self, object_name, dimension_name, attribute_name):
        """
        find and retrieves the details of an attribute

        :param object_name: the name of xobject
        :param dimension_name: the name of dimension
        :param attribute_name: the name of attribute
        :return: details of this attribute in json format
        """

        dimension = self.get_dimension_info(object_name, dimension_name)

        if dimension is not None:
            for attribute_obj in dimension['attributes']:
                if attribute_obj['attributeName'] == attribute_name:
                    return attribute_obj
            print("XAttribute " + attribute_name + " is not found")
            return None

    def get_tree_details(self, object_name=None, dimension_name=None,
                         attribute_name=None):
        """
        get the meta data details of certain xplain object, dimension or
        attribute as json

        :param object_name:  the name of object optional , if empty, show the
        whole object tree from root,  if only objectName is specified,
        this funtion will return the meta data of
                 this object
        :type    object_name: string, optional
        :param dimension_name:  the name of dimension, optional,
        it object_name and dimension_name are specified, it will return the
        dimesion meta data
        :type    dimension_name: string, optional
        :param attribute_name:  the name of attribute, optional,
        it object_name, dimension_name and attribute_name is specified,
        it will return the attribute meta data
        :type    attribute_name: string, optional
        :return: object tree details
        :rtype: json
        """

        if object_name is None and dimension_name is None and attribute_name \
                is None:
            return self.__xplain_session__['focusObject']
        if object_name != None and dimension_name is None and attribute_name \
                is None:
            return self.get_object_info(object_name)
        if object_name != None and dimension_name is not None and \
                attribute_name is None:
            return self.get_dimension_info(object_name, dimension_name)
        if object_name != None and dimension_name is not None and \
                attribute_name is not None:
            return self.get_attribute_info(object_name, dimension_name,
                                           attribute_name)

    def get_root_object(self):
        """
        get root object from the session

        :return: XObject: [description]
        """

        # return xplain.get_root_object()

    def get_xobject(self, object_name):
        """
        retrieve the xobject with the given object name

        :param object_name: string xobject name
        :return: XObject instance
        """
        # return xplain.XObject(object_name)

    def resume_analysis(self, file_name):
        """
        resume the stored session

        :param filename: name of stored session file
        :return:  False (fail) or True (success)
        :rtype: Boolean
        """
        if ".xanalysis" not in file_name:
            file_name = file_name + ".xanalysis"
        method_call = {
            "method": "resumeAnalysis",
            "fileName": file_name
        }

        self.post(method_call)

    def get_queries(self):
        """
        get the list of existing queries

        :return: the query names as list
        """
        result = []
        requests = self.__xplain_session__["requests"]
        for req in requests:
            result.append(req["requestName"])
        return result

    def refresh(self):
        response_json = self.__parseResponse__(self.get())
        self.store_xsession(response_json)

    def get_model_names(self):
        if self.get_session().get('predictiveModels') is not None:
            return list(self.get_session().get('predictiveModels').keys())

    def get_variable_list(self, model_name):
        result = []
        if self.get_session().get('predictiveModels')[model_name] is not None:
            for variable in self.get_session().get('predictiveModels')[
                model_name][
                'independentVariables']:
                result.append(variable["name"])
        else:
            print(model_name + " not found")
        return result

    def build_predictive_model(self, model_name, model_config,
                               model_object_name, significance,
                               target_event_object_name,
                               target_selection_object_name,
                               target_selection_dimension_name,
                               target_selection_attribute,
                               output_prefix=''):
        if model_config.find('.xdefaultmodel') == -1 and model_config.find(
                '.xmodel') == -1:
            model_config = model_config + '.xmodel'

        query = {
            "method": "buildPredictiveModel",
            "significance": significance,
            "modelName": model_name,
            "targetSelectionAttributes": [
                {
                    "attribute": target_selection_attribute,
                    "dimension": target_selection_dimension_name,
                    "object": target_selection_object_name
                }
            ],
            "modelObject": model_object_name,
            "xmodelConfigurationName": model_config,
            "targetEventObject": target_event_object_name
        }
        self.run(query)
        result = {}

        df_independent_var = self.load_file_as_df(str(output_prefix or '') +
                                                  model_name + str(
            '-IndependentVariables.csv'))

        df_learning_log = self.load_file_as_df(str(output_prefix or '') +
                                               model_name +
                                               '-Learning-Log.txt')

        df_observation = self.load_file_as_df(
            str(output_prefix or '') + model_name +
            "-Observations.csv")

        df_predicted_probabilities = self.load_file_as_df(
            str(output_prefix or '') +
            model_name +
            '-PredictedProbabilities.csv')
        df_roc = self.load_file_as_df(
            str(output_prefix or '') + model_name + '-ROC.csv')
        result["IndependentVariables"] = df_independent_var
        result["Learning - Log"] = df_learning_log
        result["Observation"] = df_observation
        result["PredictedProbabilities"] = df_predicted_probabilities
        result["ROC"] = df_roc
        return result

    def load_file_as_df(self, filename):
        response = requests.get(
            url=self.__url__ + '/readfile?filename=' + filename,
            cookies=self.__cookies__, verify=False)
        if response.status_code != 200:
            raise Exception("The predictive model output file " + filename + " "
                                                                             "could not be found.")
        content = response.text
        dataframe = pd.read_csv(io.StringIO(content), sep=';')
        return dataframe

    def post_file_download(self, filename, deleteAfterDownload=True, zip=True):
        """
        triggers the flat table download functionality in XOE

        :param params: request parameters for file download
        :return: http response object
        """
        params = dict(filename=filename,
                      deleteAfterDownload=deleteAfterDownload,
                      zip=zip)

        response = requests.get(self.__url__ + '/downloadfile',
                                params=params,
                                cookies=self.__cookies__,
                                headers=self.__headers__,
                                verify=False)
        return response

    def set_default_broadcast(self, broadcast):
        """
        set default broadcast to inform other xplain client to perform refresh

        """
        self.__broadcast__ = broadcast

    def open_sequence(self, target_object,
                      base_object,
                      ranks, reverse, names, name_postfixes,
                      dimensions_2_replicate, sort_dimension,
                      zero_point_dimension,
                      selections,
                      selection_set_definition_rank,
                      floating_semantics, attribute_2_copy,
                      sequence_name, rank_dimension_name,
                      rank_zero_is_first_instance_equal_or_greater_zero_point,
                      transition_attribute, transition_level,
                      open_marginal_queries,
                      open_transition_queries,
                      selection_set
                      ):
        sequence_request = dict(method="openSequence",
                                targetObject=target_object,
                                ranks=ranks,
                                reverse=reverse,
                                names=[names],
                                namePostfixes=name_postfixes,
                                dimensionsToReplicate=[dimensions_2_replicate],
                                sortDimension=sort_dimension,
                                baseObject=base_object,
                                zeroPointDimension=zero_point_dimension,
                                # selections=selections,
                                selectionSetDefiningRank=selection_set_definition_rank,
                                floatingSemantics=floating_semantics,
                                attributesToCopy=[[attribute_2_copy]],
                                sequenceNames=[sequence_name],
                                rankDimensionName=[rank_dimension_name],
                                rankZeroIsFirstInstanceEqualOrGreaterZeroPoint
                                =rank_zero_is_first_instance_equal_or_greater_zero_point,
                                transitionAttribute=transition_attribute,
                                transitionLevel=transition_level,
                                openMarginalQueries=open_marginal_queries,
                                openTransitionQueries=open_transition_queries,
                                selectionSet=selection_set
                                )

        cleaned_req = {k: v for k, v in sequence_request.items() if v is not
                       None}
        self.run(cleaned_req)

    def get_open_sequences(self, sequence_name):
        return self.__xplain_session__["openSequences"][sequence_name]

    def get_sequence_transition_matrix(self, sequence_name):
        label = []
        source = []
        target = []
        value = []
        transition_queries = self.get_open_sequences(sequence_name)[
            'transitionQueryNames']
        for transition_query_name in transition_queries:
            df = self.get_result(transition_query_name)
            col = list(df.columns)

            for index, row in df.iterrows():
                # print(row[col[0]], row[col[1]])
                source_node = col[0].split(". ")[0] + " " + row[col[0]]
                target_node = col[1].split(". ")[0] + " " + row[col[1]]

                if source_node not in label:
                    source_index = len(label)
                    label.append(source_node)
                else:
                    source_index = label.index(source_node)
                source.append(source_index)

                if target_node not in label:
                    target_index = len(label)
                    label.append(target_node)
                else:
                    target_index = label.index(target_node)
                target.append(target_index)

                value.append(row[col[2]])
        return dict(label=label, source=source, target=target, value=value)

    def gen_xtable(self, data, xtable_config, file_name):
        # content = data.to_string(header=False,
        #                         index=False,
        #                         index_names=False)
        df = data.to_csv(header=None, index=False).strip('\n').split('\n')
        df_string = '\r\n'.join(df)
        data_file = df_string.encode('utf8')

        # data_file = bytes(content, encoding='utf8')

        conf_str = json.dumps(xtable_config)
        conf_file = bytes(conf_str, encoding='utf8')

        file_name = bytes(file_name, encoding='utf8')

        with io.BytesIO() as buf:
            buf.write(data_file)
            buf.seek(0)

            requests.post(self.__url__ + "/create_xtable",
                          files={
                              "data_file": buf,
                              "xtableconfig": conf_file,
                              "file_name": file_name
                          },
                          cookies=self.__cookies__,
                          headers=self.__headers__,
                          verify=False
                          )

    def list_files(self, ownership, file_type, file_extension):
        result = None
        if file_extension is not None:
            payload = json.dumps({
                'file': {
                    'ownership': ownership,
                    'fileType': file_type,

                },
                'fileExtension': file_extension
            })
        else:
            payload = json.dumps({
                'file': {
                    'ownership': ownership,
                    'fileType': file_type
                }
            })

        response = requests.post(self.__url__ + "/list_files", data=payload,
                                 cookies=self.__cookies__,
                                 headers=self.__headers__,
                                 verify=False)
        if response.status_code == 200:
            try:
                result = json.loads(response.content)
                return result
            except:
                return response.content

        return result

    def read_file(self, ownership, file_type, file_path):
        result = None
        payload = json.dumps({
            'file': {
                'ownership': ownership,
                'fileType': file_type,
                'filePath': file_path
            }
        })
        response = requests.post(self.__url__ + "/read_file", data=payload,
                                 cookies=self.__cookies__,
                                 headers=self.__headers__,
                                 verify=False)
        if response.status_code == 200:
            try:
                result = json.loads(response.content)
                return result
            except:
                return response.content

        return result

    def validate_db(self, db_connection_config):
        payload = json.dumps({
            "databaseConnectionConfiguration": db_connection_config
        })

        response = requests.post(self.__url__ + "/db_tables",
                                 data=payload,
                                 cookies=self.__cookies__,
                                 headers=self.__headers__,
                                 verify=False)
        if response.status_code != 200:
            reasons = json.loads(response.content)
            raise Exception(reasons.get("message"))

    def run_py(self, file_name, options, ownership):
        result = None
        payload = json.dumps(
            {
                "file": {
                    "ownership": ownership,
                    "fileType": "XSCRIPT",
                    "filePath": [file_name]
                },
                "options": options
            }
        )
        response = requests.post(self.__url__ + "/run_python_file",
                                 data=payload,
                                 cookies=self.__cookies__,
                                 headers=self.__headers__,
                                 verify=False)

        if response.status_code == 200:
            try:
                result = json.loads(response.content)
                return result
            except:
                return response.content

        return result
