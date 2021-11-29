import ftplib
import getopt
import gzip
import io
import os
import re
import signal
import sys
import tarfile
import threading
import time
import requests
import argparse
import zipfile
import xml.etree.ElementTree as ET
import gzip

from contextlib import closing


def get_PMCID_path_info(pmcid, output_path):
	#using api: https://www.ncbi.nlm.nih.gov/pmc/tools/oa-service/

	##pmcid specific one: https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC5334499
	base_api = 'https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi'
	id_info_start = '?id='
	response = requests.get('%s%s%s' %(base_api, id_info_start, pmcid))  ##full text (xml string)
	with open('%s%s_%s.xml' %(output_path, 'PMCOA_INFO', pmcid), 'w+') as pmcoa_info_output_file:
		pmcoa_info_output_file.write(response.text)

	pmcoa_info_text = response.text.split(' ')
	ftp_url = None
	for info in pmcoa_info_text:
		if 'href' in info:
			ftp_url=info[info.find('ftp'):].replace('"','')
			print(ftp_url)
		else:
			pass


	if ftp_url:
		return ftp_url
	else:
		raise Exception('ERROR: The PMCID has no href for FTP stuff from the API')



def get_pmcid_FTP_download(pmcid, ftp_url, output_path):
	##https://data.lhncbc.nlm.nih.gov/public/trec-cds-org/download.py
	global pmc, requests

	archive = ftp_url.split('pmc/')[-1]
	# print(archive)

	#connect to the ftp spot
	pmc = ftplib.FTP('ftp.ncbi.nlm.nih.gov')
	pmc.login()
	pmc.cwd('/pub/pmc')

	##from extract
	# global requests, pmc
	# pmc.dir()

	response = io.BytesIO()
	tar = None
	pmc.retrbinary("RETR " + archive, response.write, 32)
	tar = tarfile.open(fileobj=io.BytesIO(response.getvalue()), mode="r:gz")
	tar.extractall(path=output_path) #,members=files_to_extract(tar, pmcid)


	# disconnect() ##disconnect from the ftp
	pmc.close()



def get_all_BioC_section_files(api_url_base, format, encoding, article, save_xml_path):

	## loop over each pmc article and grab the BioC format of the full text article local
	# for pmc_article in pmc_filename_list:
	##https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_[format]/[ID]/[encoding]
	full_url = api_url_base + format + article + encoding


	#save the resulting xml file to BioC_section_info

	with open('%s%s%s%s.xml' %(save_xml_path, article, '.nxml.gz.txt', '.BioC-full_text'), 'w') as BioC_full_text:
		#PMC1247630.nxml.gz.txt.gz.regex-sections.annot

		response = requests.get(full_url) ##full text (xml string)
		BioC_full_text.write(response.text)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument('-article_list', type=str, help='the list of articles delimited with , and no spaces between them (include PMC)')
	parser.add_argument('-PMC_FTP_output', type=str, help='the file path to the pmcoa FTP output folder')
	parser.add_argument('-PMC_BioC_output', type=str, help='the file path to the pmcoa BioC output folder')

	args = parser.parse_args()

	article_list = args.article_list.split(',')
	print(article_list)

	##Get the BioC format section info
	##https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_[format]/[ID]/[encoding]
	api_url_base = 'https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_'
	format = 'xml/'
	encoding = '/unicode'

	##get all the article information using API to then use FTP
	for pmcid in article_list:
		##get the ftp url from the API
		# ftp_url = get_PMCID_path_info(pmcid, args.PMC_FTP_output)

		##get the article package contents via FTP
		# get_pmcid_FTP_download(pmcid, ftp_url, args.PMC_FTP_output)

		get_all_BioC_section_files(api_url_base, format, encoding, pmcid, args.PMC_BioC_output)



