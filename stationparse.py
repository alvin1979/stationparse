"""
	Copyright (C) 2016 alvin <alvin1979@mail.ru>
	
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
"""

import sys
import os

import urllib
import shutil
import re

import zipfile
import tempfile
import argparse


class Radio_data:
	def __init__( self ):
		self.url 	= "http://www.radiosure.com/rsdbms/stations2.zip"
		self.file 	= None	
		self.delim  = '\t'
		self.out 	= None
		
class User_agent( urllib.FancyURLopener ):
	version = "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6"
	

radio_data = None
temp_dir = tempfile.mkdtemp()

m3u_header = "#EXTM3U\n"
args = None
data_fields = [ "title", "description", "genre", "state", "language" ]


def Promt( msg ) :
	print msg
	sys.stdin.readline()

def Clean() :
	try:
		if radio_data.out :
			radio_data.out.flush()
			radio_data.out.close()
		
		
		if radio_data.file : 
			radio_data.file.close()
		
		shutil.rmtree( temp_dir, True )
	except:
		pass
	
def Read_args() :
	try:
		global args
		
		parser = argparse.ArgumentParser( "Parse radiosure.com stations data into m3u playlist" )
		
		parser.add_argument( "--input", type = str, help = "local path to zip file of radiosure.com stations data" )
		parser.add_argument( "--out", 	type = str, help = "path, where stations playlist will be stored" )
		parser.add_argument( "--regx", 	type = str, help = "regular expression based filter (e.g., --regx .*rock.*)" )
		parser.add_argument( "--smax", 	type = int, default = 1, help = "maximum number of streams per single station to be outputted" )
		
		for field in data_fields :
			parser.add_argument( "--" + field, 	type = str, help = "filter by station {}".format( field ) )
		
		args = parser.parse_args()
		
	except:
		sys.exit( 1 )

def Filter( subs, orig ) : 
	out_stream_list = []
	i = 0
	
	if args.regx and not re.compile( args.regx ).search( orig ) :
			return out_stream_list
	
	for i, field in enumerate( data_fields ) :
		if args.__dict__[ field ] and ( args.__dict__[ field ].lower() not in subs[ i ].lower() ) :
			return out_stream_list

	data_fields_n = len( data_fields )
	stream_n = len( subs ) - data_fields_n	
	
	for i in range( stream_n ) :
		if i >= args.smax :
			break
		station = subs[ data_fields_n + i ]
		if len( station ) > 3 : 
			out_stream_list.append( station )
	
	return out_stream_list
		
def Parse_station( str, delim ) :
	subs = str.split( delim )
	
	streams_list = Filter( subs, str )
	
	out = ""
	
	i = 0
	if len( streams_list ) > 1 :
		for stream in streams_list :
			i += 1
			out += "#EXTINF:-1,{0[0]} - {0[1]} {2}\n{1}\n".format( subs, stream, i )
	elif len( streams_list ) != 0 :
		out = "#EXTINF:-1,{0[0]} - {0[1]}\n{1}\n".format( subs, streams_list[ 0 ] )

	return out

def Load_station_db() :
	if not args.input :
		with zipfile.ZipFile( urllib.urlretrieve( radio_data.url )[ 0 ], 'r' ) as zip :	
			zip.extractall( temp_dir )
			radio_data.file = open( os.path.join( temp_dir, zip.namelist()[ 0 ] ), 'r' )
	else :
		radio_data.file = open( args.input, 'r' )
	
def Output( data ) :	
	if radio_data.out :
		radio_data.out.write( data )
	else :
		print data
		
def Main():
	global radio_data 
	
	radio_data = Radio_data()
	
	urllib._urlopener = User_agent()
	
	try:
		Read_args()	
		
		Load_station_db()
		
		if args.out : 
			radio_data.out = open( args.out, 'w' )
			
		Output( m3u_header )
		for station_str in radio_data.file:
			parsed = Parse_station( station_str, radio_data.delim )
			if len( parsed ) != 0 : 
				Output( parsed )
			

	except:
		Promt( "error retrieving station data" )
	finally:
		Clean()
	
if __name__ == "__main__":	
	Main()