" File:  "Walk.vim" 
" Last Change: 2003/11/24 16:49:37 .
" Author: Jean-Christophe Clavier <jcclavier{at}free.fr>
" Version: 0.7
"
" This plugin intends to provide facilities to manage sets of files. For
" example :
" . to create files from visited directory trees and files
" . to apply Vim commands on opened files
" In fact, it autorizes files and dirs manipulation in many ways
"
" As this plugin can manage many parameters, i decided to put these parameters
" in an ini file. Doing so allows you to deal with many mass treatments.
" In this ini file, you can specify
" . a set of root dirs which trees will be visited. For Each root dir, you can
"   define other parameters you estimate useful
" . Parameters that contain strings to be written in the outfile :
"   . at begining and end of the file (can be connect string for command
"     files)
"   . entering and going out the root dirs
"   . entering and going out the visited dirs
"   . before and after the files found
"   These parameters can contain vim commands (between {{...}}) so you can do
"   whatever you want with the file names
" . You also have parameters that define
"   . a wildcard to filter the files
"   . a vim command to apply to the files found
"     This command may be written in the iniFile but may also be passed as a
"     parameter of the Walk command. If one command is written in the ini file
"     and another is passed to the Walk command, the inifile one is
"     overwritten by the parameter
"     If you want a result to be written in the outfile, this result may be
"     written in the "o" register
"   . the name of the outfile
" You've got a complete example of ini file (example.ini) that can be used to
" see how this plugin reacts. You just have to modify <SourceDir> and
" <OutFile> parameter.
" Other iniFile examples have been put in the package :
" . One is to generate a tag file with the names of the files found (exTagGen)
" . Another is to generate a file to prepare a syntax file to color the names
"   of the files found (to be used after exTagGen) (exColTagGen)
"   This is not very useful for source files but may be interesting to manage
"   simple text files with cross references
" . The last is to generate a directory tree (good for CDs' TOC) (exTreeGen)
"
" The name of the ini files to use is to be stocked in the "i" register. You
" can put more than one file in the register. They will all be used.
"
" Warning :
" These registers are used by this plugin
" o, i, f
"
" Features
" WGoIniDir     : Change the current dir to the inifiles dir. This is to ease
"                 manipulation of inifiles
" WSetIniFile   : Initialise the "i" register with the filename passed
" WAddIniFile   : Add the filename passed to the "i" register
" WEditIniFile  : edits the inifile which name in passed. If this file is
"                 empty, it is initialized with the content of "skeleton.ini"
"
" Walk          : launch the action, taking the inifiles wich names are
"                 written in the "i" register. Walk accepts an optional
"                 parameter that contains a vim command to be applied on the
"                 files found. A powerful way of using this is to define
"                 user-commands (:help user-commands)
"
" There is other ways to launch the walk operation : you can call the walk
" function that way :
" :call Walk(cmd,inifile)
" All the arguments must be provided (with no completion).
" :call Walk("",iniFile)
" You can write more than one ini files in the "i" register and type
" :call Walk("","") or
" :call Walk(cmd,"")
"
" Note : if you use the windows way of calling directories (with \), you must
" be careful : you have to write
" :call Walk(cmd,'D:\my\directory\myIniFile.ini')
" or
" :call Walk(cmd,"D:\\my\\directory\\myIniFile.ini")
"
" Installation
" Warning : this plugin uses python
"
" It is made of three files : Walk.vim, Walk.py and FicIni.py.
" The .vim file is to be dropped in the plugins directory and the .py
" in a directory declared in the python path by a little
" let $PYTHONPATH=$PYTHONPATH . "/MyDirectory/Python"
" in your .vimrc
"
" you also have an .ini file examples (example.ini, exTagGen.ini,
" exColTagGen.ini and exTreeGen) and a skeleton for .ini files (skeleton.ini).
" These files are to be dropped in an inifiles directory (you decide).
" Skeleton.ini is used by the WEditIniFile command.
" To use the examples, you'll have to edit them to change the <SourceDir> and
" the <OutFile> parameter
"
" To ease the edition of the ini files, you have to init another variable in
" your .vimrc ($WALKINIDIR):
" let $WALKINIDIR = "MyDirectory/iniFiles"
" 
" NOTE:
" FicIni.py provides a class to parse xml ini files (details in FicIni.py)
"
" Line continuation used here
if exists("loaded_Walk") && !exists('g:force_load_Walk')
  finish
endif
let loaded_Walk = 1

let s:cpo_save = &cpo
set cpo&vim


if !exists(':Walk')
    command -complete=command -nargs=? Walk call s:CmdWalk(<f-args>)
endif
if !exists(':WSetIniFile')
    command -complete=file -nargs=1 WSetIniFile call s:WSetIniFile(<f-args>)
endif
if !exists(':WAddIniFile')
    command -complete=file -nargs=1 WAddIniFile call s:WAddIniFile(<f-args>)
endif
if !exists(':WEditIniFile')
    command -complete=file -nargs=1 WEditIniFile call s:WEditIniFile(<f-args>)
endif
if !exists(':WGoIniDir')
    command WGoIniDir chd $WALKINIDIR
endif

function! s:WEditIniFile(...)
    let g:walkIniFiles=$WALKINIDIR . "/" . a:1
    exe "e " . g:walkIniFiles
    if line("$")==1
        exe "read " . $WALKINIDIR . "/skeleton.ini"
    endif
    set ft=xml
endfunction

function! s:WSetIniFile(...)
    let g:walkIniFiles=$WALKINIDIR . "/" . a:1
endfunction

function! s:WAddIniFile(...)
    if !exists('g:walkIniFiles')
        let g:walkIniFiles=$WALKINIDIR . "/" . a:1
    else
        let g:walkIniFiles=g:walkIniFiles . "\n" . $WALKINIDIR . "/" . a:1
    endif
endfunction

function! Walk(cmd, iniFile)
    " Calls the Python function that visits a directory tree and applies the
    " VIM command passed to the files filtered by the wildcard
    " root directories and other arguments are in the iniFile which name is in
    " the i register
    "
    if a:iniFile != ""
        let s:iniFile=substitute(a:iniFile,"\\","\\\\","")
    else
        let s:iniFile=substitute(g:walkIniFiles,"\\","\\\\","")
    endif
    split
python << EOS
from Walk import *
iniFiles=string.split(vim.eval("s:iniFile"),"\n")
for iniFile in iniFiles:
    vw=Walk(iniFile)
    vw.walk(vim.eval("a:cmd"))
EOS
endfunction

function! s:CmdWalk(...)
    if a:0 >= 1
        let s:i = 1
        let s:arg = ""
        while s:i <= a:0
            let s:arg = s:arg . ' ' . a:{s:i}
            let s:i = s:i + 1
        endwhile
        call Walk(s:arg,"")
    else
        call Walk("","")
    endif
endfunction

" restore 'cpo'
let &cpo = s:cpo_save
unlet s:cpo_save

