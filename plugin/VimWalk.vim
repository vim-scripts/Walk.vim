" File:  "VimWalk.vim" Last modified : 2003/10/20 11:05:36 .
" Author: Jean-Christophe Clavier (jcclavier@free.Fr)
" Version: 0.1
"
" This plugin permits to visit a set of directory trees, filter the files with
" a wildcard and apply a VIM command to the files found.
"
" If some informations have to be written in an out file, simply write these
" informations in the "o" register during the VIM command to apply
"
" This plugin is given with an example (WkTest) which writes the first line of
" each visited file in the outfile.
" To launch this command on all the files of a directory tree, simply type :
" :Walk WkTest
"
" Roots directories to visit are written in the "d" register. If you have
"       several trees to visit, the roots must be separated by an '\n'
" Wildcard is written in the "w" register
" The content of register "o" is written in the file which name is written in
"       "f" register
"
" Arguments are passed through registers instead of classical argument passing
" to ease the typing (initialisation can be done with a command called each
" time one want to deal with a particular set of directories)
"
" If no command is provided to Walk, the outfile contains the file list
"
" Installation
" Warning : This plugin uses Python.
"   It doesn't seem to like when the VIM command passed uses python either.
"
" It is made of two files : VimWalk.vim et VimWalk.py.
" VimWalk.vim is to be dropped in the plugins directory and VimWalk.py
" in a directory declared in the python path :
" let $PYTHONPATH=$PYTHONPATH . "/MyDirectory/Python"
" in .vimrc
"
" These mapping may be useful to copy the content of the clipboard in the
" wanted register
" map _w let @w=@*
" map _d let @d=@*
" map _f let @f=@*
"
"
" Line continuation used here
let s:cpo_save = &cpo
set cpo&vim


if !exists(':Walk')
    command -complete=command -nargs=? Walk call s:Walk(<f-args>)
endif

if !exists(':WkTest')
    command WkTest call s:WkTest()
endif

function! s:WkTest()
    norm ggV"oy
endfunction

function! s:Walk(...)
    " Calls the Python function that visits a directory tree and applies the
    " VIM command passed to the files filtered by the wildcard
    " Roots directories to visit are written in th "d" register. If you have
    "       several trees to visit, the roots must be separated by an '\n'
    " Wildcard is written in the "w" register
    " The content of register "o" is written in the file which name is written in
    "       "f" register

    python from VimWalk import *
    " Default value
    if @w == ""
        let @w = "."
    endif
    if a:0 == 1
        python argmt = vim.eval("a:1")
    else
        python argmt = ''
    endif
    python vw=VimWalk(argmt)
endfunction

" restore 'cpo'
let &cpo = s:cpo_save
unlet s:cpo_save

