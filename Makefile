# Makefile for source rpm: guile
# $Id$
NAME := guile
SPECFILE = $(firstword $(wildcard *.spec))

include ../common/Makefile.common
