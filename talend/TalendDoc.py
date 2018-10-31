import pprint
import json
import os
import sys
from xml.dom import minidom
from git import Repo
import functools
import git


class TalendDoc:

    def __init__(self, path):
        self.path = path
        self.copyPath = None
        self.repo = None

    def get_jobs(self):
        dir = {}
        jobsPath = os.path.join(self.copyPath, 'process')
        rootdir = jobsPath.rstrip(os.sep)
        start = rootdir.rfind(os.sep) + 1
        for path, dirs, files in os.walk(rootdir):
            folders = path[start:].split(os.sep)

            subdir = dict.fromkeys(files)
            parent = functools.reduce(dict.get, folders[:-1], dir)

            jobs = {}
            for file in subdir:
                if file[-5:] == ".item":
                    jobName = file[0:file.rfind('_')]
                    if jobName not in jobs:
                        jobs[jobName] = {
                            'isJob': True,
                            'name': jobName,
                            'versions': {}
                        }
                    version = file[file.rfind('_')+1:file.rfind('.')]
                    try:
                        job = self.get_job(path, jobName, version)
                    except Exception as ex:
                        print('Job Parsing Error, ', path, jobName, version)
                        raise ex

                    jobs[jobName]['versions'][version] = job

            parent[folders[-1]] = jobs
            # parent[folders[-1]] = subdir
        return dir

    def get_job(self, path, jobName, version):
        xmlItemPath = os.path.join(self.copyPath, path, jobName+'_'+version+'.item')
        itemXml = minidom.parse(xmlItemPath)

        jobParameters = {}
        parameters = itemXml.getElementsByTagName("parameters")[0].getElementsByTagName('elementParameter')
        for p in parameters:

            jobParameters[p.getAttribute('name')] = {'value': p.getAttribute('value')}

        nodes = itemXml.getElementsByTagName("node")
        components = []
        for node in nodes:
            component = {}
            component['name'] = node.getAttribute('componentName')
            component['version'] = node.getAttribute('componentVersion')
            component['offsetLabelX'] = node.getAttribute('offsetLabelX')
            component['offsetLabelY'] = node.getAttribute('offsetLabelY')
            component['posX'] = node.getAttribute('posX')
            component['posY'] = node.getAttribute('posY')
            component['parameters'] = {}
            parameters = node.getElementsByTagName('elementParameter')
            for parameter in parameters:
                parameterName = parameter.getAttribute('name')
                discardedParameters = ['JAVA_LIBRARY_PATH', 'CONNECTION_FORMAT', 'UNIQUE_NAME']
                if parameterName not in discardedParameters:
                    component['parameters'][parameterName] = {'value': parameter.getAttribute('value')}
                if parameterName == 'UNIQUE_NAME':
                    component['unique_name'] = parameter.getAttribute('value')
            components.append(component)

        screenshotXmlPath = os.path.join(self.copyPath, path, jobName+'_'+version+'.screenshot')
        screenshotXml = minidom.parse(screenshotXmlPath)
        screenshots = screenshotXml.getElementsByTagName("talendfile:ScreenshotsMap")

        if len(screenshots):
            screenshot = screenshots[0].getAttribute('value')
        else:
            screenshot = 'R0lGODlh0wD8AMQAAGZmZoiIiP/v7/8PD//Pz/+vr/8vL/9PT/9/f/8fH+7u7v+/v/9vb8zMzBEREf8/P//f30RERN3d3aqqqv+PjyIiIpmZmTMzM3d3d1VVVf9fX7u7u/+fnwAAAP8AAP///yH/C1hNUCBEYXRhWE1QPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNS4wLWMwNjAgNjEuMTM0Nzc3LCAyMDEwLzAyLzEyLTE3OjMyOjAwICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtbG5zOnhtcE1NPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvbW0vIiB4bWxuczpzdFJlZj0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL3NUeXBlL1Jlc291cmNlUmVmIyIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ1M1IFdpbmRvd3MiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6NDlBNTlERjM5Q0JDMTFFMzgzOTVGRDE0RjBCMDk2MjciIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6NDlBNTlERjQ5Q0JDMTFFMzgzOTVGRDE0RjBCMDk2MjciPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDo0OUE1OURGMTlDQkMxMUUzODM5NUZEMTRGMEIwOTYyNyIgc3RSZWY6ZG9jdW1lbnRJRD0ieG1wLmRpZDo0OUE1OURGMjlDQkMxMUUzODM5NUZEMTRGMEIwOTYyNyIvPiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gPD94cGFja2V0IGVuZD0iciI/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'

        job = {
            'screenshots': screenshot,

            'components': components,
            'parameters': jobParameters
        }
        return job

    # def clone_repo(self):
    #

    def get_local_copy(self):
        repoName = self.path[self.path.rfind('/')+1:]
        repoName = repoName[0:repoName.rfind('.')]
        self.copyPath = os.path.join(os.getcwd(), "data", repoName)

        if os.path.isdir(self.copyPath):
            repo = Repo(self.copyPath)
            origin = repo.remotes.origin
            origin.fetch()
            origin.pull()
            self.repo = repo
        else:
            Repo.clone_from(self.path, self.copyPath, depth=1)
            self.repo = Repo(self.copyPath)

    def parse(self):
        self.get_local_copy()

        xmldoc = minidom.parse(os.path.join(self.copyPath, "talend.project"))
        project = xmldoc.getElementsByTagName("TalendProperties:Project")[0]

        doc = {
            'metadata': {
                'path': self.copyPath
            },
            'name': project.getAttribute('label'),
            'language': project.getAttribute('language'),
            'product_version': project.getAttribute('productVersion'),
            'jobs': self.get_jobs(),
            'repo': self.repo
        }
        return doc
