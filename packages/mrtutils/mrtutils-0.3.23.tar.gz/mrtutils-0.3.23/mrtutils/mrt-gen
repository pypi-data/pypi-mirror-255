#!/usr/bin/env python

import sys
import os
from mrtutils.mrtTemplateHelper import *
from mrtutils.mrtDocHelper import DocHelper
from mako.template import Template
import argparse
from datetime import date
import getpass



args = None
parser = None


def copyFile( srcfile, outputFile):
    src_data = pkgutil.get_data('mrtutils',srcfile)
    dst = open( outputFile , "wb")
    dst.write(src_data)
    dst.close()
    print("Created " + outputFile)


def buildTemplate(object, templateFile, outputFile, replacePattern = r"@file (.*?\.)(.*?) \*/"):
    exists= False
    cr = CodeReplacer()
    newContents =""
    if os.path.isfile(outputFile):
        exists = True
        curFile = open(outputFile, "r")
        text = curFile.read()
        cr.loadText(text)
        cr.loadText(text,replacePattern)

    template = Template(pkgutil.get_data('mrtutils',templateFile) )
    newContents = "\n".join(template.render(obj = object, t = TemplateHelper()).splitlines())
    newContents = cr.insertBlocks(newContents)
    newContents = cr.insertBlocks(newContents,replacePattern)
    cr.printDrops()
    text_file = open( outputFile , "w")
    text_file.write(newContents)
    text_file.close()
    print("Created " + outputFile)

# Initialize the argument parser
def init_args():
    global parser
    parser = argparse.ArgumentParser("Tool to generate code snippets and components")
    parser.add_argument('path', type=str, nargs='?', help='generation path', default="")
    parser.add_argument('-t', '--type', type=str, help='Generation type [c,cpp,doc, vue]', default="")
    parser.add_argument('-d', '--desc', type=str, help='description', default="")
    parser.add_argument('-m', '--module', action='store_true', help='Generates mrt module', default=False)


def gen_c_files(obj):
    os.makedirs(obj.path,exist_ok=True) 
    buildTemplate(obj, "templates/gen/c.h", obj.path + "/" + obj.name +".h")
    buildTemplate(obj, "templates/gen/c.c", obj.path + "/" + obj.name +".c")

def gen_cpp_files(obj):
    os.makedirs(obj.path,exist_ok=True) 
    buildTemplate(obj, "templates/gen/c.h", obj.path +"/" + obj.name +".h")
    buildTemplate(obj, "templates/gen/cpp.cpp", obj.path +"/" + obj.name +".cpp")

def gen_doc_structure(obj):
    os.makedirs(obj.path,exist_ok=True) 
    d = DocHelper() 

    d.buildDocStructure(obj.path + "/" + obj.name)



def gen_mrt_mod(obj):

    os.makedirs(obj.path,exist_ok=True) 
    buildTemplate(obj, "templates/gen/c.h", obj.path + "/" + obj.name +".h")
    buildTemplate(obj, "templates/gen/c.c", obj.path + "/" + obj.name +".c")
    buildTemplate(obj, "templates/gen/README.rst", obj.path + "/README.rst")
    buildTemplate(obj, "templates/gen/mrt.yml", obj.path + "/mrt.yml")
    buildTemplate(obj, "templates/gen/UT.cpp", obj.path +"/"+ obj.name + "_UT.cpp")
    
#Generate a single file vue component 
def gen_vue_file(obj):
    os.makedirs(obj.path,exist_ok=True) 
    buildTemplate(obj, "templates/gen/vue/vue-single.vue", obj.path + "/" + obj.name + ".vue")

def gen_vue_component(obj):
    os.makedirs(obj.path , exist_ok=True)
    buildTemplate(obj, "templates/gen/vue/vue.vue", obj.path + "/" + obj.name + ".vue")
    buildTemplate(obj, "templates/gen/vue/vue.html", obj.path + "/" + obj.name +  ".html")
    buildTemplate(obj, "templates/gen/vue/vue.ts", obj.path + "/" + obj.name + ".ts")
    buildTemplate(obj, "templates/gen/vue/vue.css", obj.path + "/" + obj.name + ".css")





class config:
    def __init__(self, path):
        self.path = path.rsplit('/', 1)[0]
        self.name = path.rsplit('/',1)[1].split('.')[0]
        self.gentime = date.today().strftime("%m/%d/%y")
        self.user = getpass.getuser()
        self.desc = ""
        self.type = ""

def main():

    global parser
    global args


    init_args()
    args= parser.parse_args()

    obj = config(args.path)
    obj.desc = args.desc
    obj.type = args.type

    #if type isnt specified
    if obj.type == "":

        #check if path has extension 
        splitpath = args.path.split('.') 

        if len(splitpath) > 1: 

            pathNoExt = splitpath[0]

            ext = args.path.replace(pathNoExt + ".", "")
            print(ext)

            print("Inferred type: " + ext)
            print(pathNoExt)
            obj = config(pathNoExt)
            obj.desc = args.desc
            obj.type = ext
        #if path ends in doc ie ./project/doc, assume doc generation
        elif obj.name in ['doc', 'docs']:
            obj.type = 'doc'
        else: #otherwise default to c
            obj.type = 'c'
    
    if args.module:
        obj.type = "mod"

        
    print(obj.path)
    print(obj.name)

    switcher = {
        "c": gen_c_files,
        "cpp": gen_cpp_files,
        "doc": gen_doc_structure,
        "mod": gen_mrt_mod,
        "vue": gen_vue_file,
        "comp.vue" : gen_vue_component
    }

    
    func = switcher.get(obj.type)

    func(obj)



        

if __name__ == "__main__":
    main()