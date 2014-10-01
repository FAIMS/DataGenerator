# Performance Data generator for FAIMS 2 databases
# This requires loremipsum. sudo pip install loremipsum
# This requires pillow.
# This requires espeak (apt-get), lame (apt-get)
# This requires matplotlib
# This requires pypdf2

import sqlite3, sys
from loremipsum import get_sentences
from xml.dom import minidom
from lxml import etree
import random
import numpy
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
import subprocess

import matplotlib.animation as animation
import pylab
from uuid import uuid4
import os
import shutil
from reportlab.pdfgen import canvas
import md5
import hashlib
import tarfile
import json
import sys


toCreate = { 'Entities':{ 'small' : { 'amount':1000,
									  'spatial': None,
									  'historyDoublings': 4,
									  'historyVariation': 2,
									  'nullRate': 0.2,
									  'certaintyRate': 0.2,
									  'annotationRate': 0.2,
									  'deletedRate': 0.2,
									  'multiVocabHitRate': 0.2,
									  

									  'averageFilesPerRecord': 1,
									  'fileVariationPerRecord': 0,
									  'pictureAttribute': ['picture'], # set to empty set if no pictures
									  'videoAttribute': ['video'],
									  'audioAttribute': ['audio'],
									  'fileAttribute' : ['file'],
									  'pictureHorizResolution': 2560,
									  'pictureVertResolution': 1920,									  
									  'makeCounter': ['entity'],	
									  'faimsSync': True,
									  'makeThumbnail': True
									  }
						},
		 'Relns':   { 'AboveBelow': {
							'parent': 'small',
							'child': 'small',
							'useParticipateVerbs': True,
							'avgAmountPerParent': 1,
							'variationPerRecord': 0,
							'deletedRate': 0.2
							} 
					} 
		}


'''
	Picture, original
		saved to either files/app/
						files/server/

	filename in measure

	check in attributekey if AttributeIsFile is true 
		if attributeusethumbnail is true
			save original as per e-mail
				if filesycn on:
					to files/app/UUID-<filename>.original.(jpg|mp4)
					save thumbnail to
					to files/app/UUID-<filename>.thumbnail.jpg
						thunbnail resolution is: 10% of original
				else
					s/app/server
		else
			save files/app/UUID-<filename>.(jpg|mp4)



 
'''

class AutoVivification(dict):
	"""Implementation of perl's autovivification feature."""
	def __getitem__(self, item):
		try:
			return dict.__getitem__(self, item)
		except KeyError:
			value = self[item] = type(self)()
			return value
	def replace(self, foo, bar):
	  return ''




def createImage(entity, text, filename, thumbnail, faimsSync):
	h = toCreate['Entities'][entity]['pictureVertResolution']
	w = toCreate['Entities'][entity]['pictureHorizResolution']
	img = Image.open("samplePicture.jpg")
	draw = ImageDraw.Draw(img)
	font = ImageFont.truetype("/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-L.ttf", int(h*.2))
	draw.text((h*.2, w*.2),text,(random.randint(0,255),random.randint(0,255),random.randint(0,255)),font=font)
	photoUuid = uuid4()
	if faimsSync:
		path = 'files/app/'
	else:
		path = 'files/server/'

	if thumbnail:
		img.save('%s%s_%s.original.jpg' % (path,photoUuid, filename))
		img.thumbnail((w*.1, h*.1), Image.ANTIALIAS)
		img.save('%s%s_%s.thumbnail.jpg' % (path,photoUuid, filename))
		return '%s%s_%s.original.jpg' % (path, photoUuid, filename)
	else:
		img.save('%s,%s_%s.jpg' % (path,photoUuid, filename))
		return '%s,%s_%s.jpg' % (path,photoUuid, filename)


def createMP3(text, filename, faimsSync):
	if faimsSync:
		path = 'files/app/'
	else:
		path = 'files/server/'
	photoUuid = uuid4()		
	subprocess.call(["espeak", text,"-w /tmp/espeak.wav"])
	subprocess.call(["lame", "--silent", "/tmp/espeak.wav", "%s%s_%s.mp3" % (path,photoUuid,filename)])
	return "%s%s_%s.mp3" % (path,photoUuid,filename)




dpi = 200

def createMP4(text, filename, thumbnail, faimsSync):
	fig = pylab.plt.figure()
	fig.suptitle(text)
	ax = fig.add_subplot(111)
	ax.set_aspect('equal')
	ax.get_xaxis().set_visible(False)
	ax.get_yaxis().set_visible(False)

	im = ax.imshow(numpy.random.rand(300,300),cmap='gray',interpolation='nearest')
	im.set_clim([0,1])
	fig.set_size_inches([3,3])


	pylab.tight_layout()
	if faimsSync:
		path = 'files/app/'
	else:
		path = 'files/server/'

	def update_img(n):    	
		tmp = numpy.random.rand(300,300)
		im.set_data(tmp)
		return im

	#legend(loc=0)
	photoUuid = uuid4()		
	if thumbnail:
		fig.savefig("%s%s_%s.thumbnail.jpg" % (path,photoUuid,filename))
	ani = animation.FuncAnimation(fig,update_img,20,interval=3)
	writer = animation.writers['ffmpeg'](fps=3)

	ani.save('%s%s_%s.mp4' % (path,photoUuid,filename),writer=writer,dpi=dpi)
	pylab.plt.close()
	return "%s%s_%s.mp4" % (path,photoUuid,filename)

	

def createPDF(text, filename, faimsSync):
	point = 1
	inch = 72
	title = filename
	np = 1
	if faimsSync:
		path = 'files/app/'
	else:
		path = 'files/server/'
	photoUuid = uuid4()	
	c = canvas.Canvas("%s%s_%s.pdf" % (path,photoUuid,filename), pagesize=(8.5 * inch, 11 * inch))
	c.setStrokeColorRGB(0,0,0)
	c.setFillColorRGB(0,0,0)
	c.setFont("Helvetica", 12 * point) 
	for pn in range(1, np + 1):
		v = 10 * inch
		for subtline in (text).split( '\n' ):
			c.drawString( 1 * inch, v, subtline )
			v -= 12 * point
		c.showPage()
	c.save()
	return "%s%s_%s.pdf" % (path,photoUuid,filename)

if os.path.exists('files/app'):
	shutil.rmtree('files/app')
if os.path.exists('files/server'):
	shutil.rmtree('files/server')
os.makedirs('files/app')
os.makedirs('files/server')




con = sqlite3.connect('db.sqlite3')
con.enable_load_extension(True)
con.load_extension("libspatialite.so.5")

prep = con.cursor()

prep.executescript('''
				   drop view if exists rtimestamp;
				  create view rtimestamp as 
select epoch, datetime(epoch, 'unixepoch') as timestamp from
(
SELECT strftime('%s', '2000-01-01 00:00:00') +
				abs(random() % (strftime('%s', '2014-01-31 23:59:59') -
								strftime('%s', '2000-01-01 00:00:00'))
				   ) as epoch);

				   ''')





def uuid(userid, epoch):
	return "1%05d%010d%03d" % (userid, epoch, random.randint(0,999))
con.create_function("makeuuid", 2, uuid)



print ' '.join(get_sentences(5))
# Sanity check: Are all the tables in toCreate present?

sanCheck = con.cursor()

for row in sanCheck.execute('select aenttypename from aenttype union select relntypename from relntype'):
	if row[0] in toCreate['Entities'].keys() + toCreate['Relns'].keys():
		print "Found: "+row[0] 
	else:
		print "toCreate doesn't match: "+row[0]
		sys.exit(1)



xmldoc = minidom.parse('data_schema.xml')
itemlist = xmldoc.getElementsByTagName('ArchaeologicalElement') 
archent = AutoVivification()
def recursive_dict(element):
	 return element.tag, \
			dict(map(recursive_dict, element)) or element.text

# print dir
for s in itemlist :    
  p = s.getElementsByTagName('property')
  for (idx, e) in enumerate(p):
	if s.hasAttribute('name'):
	  archent[s.attributes['name'].value][e.attributes['name'].value] = {'name':e.attributes['name'].value, 'isIdent':True if e.hasAttribute('isIdentifier') else False }
	else:
	  archent[s.attributes['type'].value][e.attributes['name'].value] = {'name':e.attributes['name'].value, 'isIdent':True if e.hasAttribute('isIdentifier') else False}

sqlBatch = ['delete from archentity;', 'delete from aentvalue;', 'delete from relationship;', 'delete from aentreln;']

useridList = con.cursor().execute('select userid from user;').fetchall()




for entity in toCreate['Entities']:
	print "making: %s %s\n\t" % (entity, toCreate['Entities'][entity])
	aenttypequery = con.cursor()
	aenttypeid = aenttypequery.execute('select aenttypeid from aenttype where aenttypename = ?', [entity]).fetchone()[0]
	

	for i in range(0,toCreate['Entities'][entity]['amount']):
		sqlBatch.append("INSERT INTO ArchEntity (uuid, aenttimestamp, deleted, userid, aenttypeid) select makeuuid(userid, epoch), timestamp, %s, userid, %s from rtimestamp, user order by random() limit 1;" % ("'true'" if random.random() <= toCreate['Entities'][entity]['deletedRate'] else "null" , aenttypeid))

	for i in range(0,toCreate['Entities'][entity]['historyDoublings']):
		sqlBatch.append("INSERT INTO ArchEntity (uuid, aenttimestamp, deleted, userid, aenttypeid) select distinct uuid, timestamp, %s, userid, aenttypeid from rtimestamp, archentity where aenttypeid = %s;" % ("'true'" if random.random() <= toCreate['Entities'][entity]['deletedRate'] else "null" , aenttypeid))

	
	con.cursor().executescript("\n".join(sqlBatch))
	sqlData = []
	sqlIdent = []

	for attrib in toCreate['Entities'][entity]['makeCounter']:
		attributeid = aenttypequery.execute('select attributeid from attributekey where attributename = ?', [attrib]).fetchone()[0]	
		for idx, uuid in enumerate(con.cursor().execute('''select distinct uuid from archentity;''')):		
			random.shuffle(useridList)	
			sqlIdent.append("INSERT INTO aentvalue (uuid, attributeid, userid, measure) values( %s, %s, %s, '%s'); " % (uuid[0], attributeid, useridList[0][0], "%s: %s" %( entity, idx) ))	
	con.cursor().executescript("\n".join(sqlIdent))


uidoc = etree.parse("ui_schema.xml")

tabgroups = uidoc.xpath("//*[@faims_attribute_name]")

print "Making values"
numTabgroups = len(tabgroups)
for numElement, element in enumerate(tabgroups):
	parent = element.xpath("ancestor-or-self::*/@faims_archent_type")
	if len(parent) >0:		
		self =  dict(element.items())
		
		for idx, uuid in enumerate(con.cursor().execute('''select distinct uuid from archentity;''')):
			if idx % 10 == 0:
				sys.stdout.write(".")			
			if random.random() >= toCreate['Entities'][entity]['nullRate']:
				attributeid = aenttypequery.execute('select attributeid from attributekey where attributename = ?', [self['faims_attribute_name']]).fetchone()[0]
				measure = ' '.join(get_sentences(2))
				certainty = 1 if random.random() >= toCreate['Entities'][entity]['certaintyRate']  else random.random()
				if random.random() <= toCreate['Entities'][entity]['annotationRate']:
					annotation = ' '.join(get_sentences(5))
				else:
					annotation = ''

				if random.random() <= toCreate['Entities'][entity]['deletedRate']:
					deleted = "'true'"
				else:
					deleted = 'null'				
				random.shuffle(useridList)
				aentvaluetimestamp = con.cursor().execute('select timestamp from rtimestamp;').fetchone()[0]
				# print self
				if self['faims_attribute_type'] == 'measure' and 'type' not in self:							
					sqlData.append("INSERT INTO aentvalue (uuid, attributeid, valuetimestamp, userid, measure, certainty, freetext, deleted) values( %s, %s, '%s', %s, '%s', '%s', '%s', %s);" % (uuid[0], attributeid, aentvaluetimestamp, useridList[0][0], measure, certainty, annotation, deleted))
				elif self['faims_attribute_type']	== 'vocab' and 'type' not in self:					
					for idx, vocabid in enumerate(con.cursor().execute('select vocabid from vocabulary where attributeid=? order by random()', [attributeid])):
						if (idx > 0 and random.random() <= toCreate['Entities'][entity]['multiVocabHitRate']) or idx == 0:
							sqlData.append("INSERT INTO aentvalue (uuid, attributeid, valuetimestamp, userid, certainty, freetext, deleted, vocabid) values(%s, %s, '%s', %s, %s, '%s', %s, %s);" % (uuid[0], attributeid, aentvaluetimestamp, useridList[0][0], certainty, annotation, deleted, vocabid[0]))
							certainty = 1 if random.random() >= toCreate['Entities'][entity]['certaintyRate'] else random.random()
							if random.random() <= toCreate['Entities'][entity]['annotationRate']:
								annotation = ' '.join(get_sentences(5))
							else:
								annotation = ''

							if random.random() <= toCreate['Entities'][entity]['deletedRate']:
								deleted = "'true'"
							else:
								deleted = 'null'	
				elif 'type' in self:
					certainty = 1 if random.random() >= toCreate['Entities'][entity]['certaintyRate'] else random.random()
					if random.random() <= toCreate['Entities'][entity]['annotationRate']:
						annotation = ' '.join(get_sentences(5))
					else:
						annotation = ''

					if random.random() <= toCreate['Entities'][entity]['deletedRate']:
						deleted = "'true'"
					else:
						deleted = 'null'

					if self['faims_attribute_name'] in toCreate['Entities'][entity]['pictureAttribute']:
						for i in range(0,random.randint(toCreate['Entities'][entity]['averageFilesPerRecord']-toCreate['Entities'][entity]['fileVariationPerRecord'],toCreate['Entities'][entity]['averageFilesPerRecord']+toCreate['Entities'][entity]['fileVariationPerRecord'])):
							entityIsIdent = con.cursor().execute("select group_concat(measure) from latestNonDeletedArchEntIdentifiers where uuid = %s group by uuid;" % (uuid[0])).fetchone()
							if entityIsIdent:
								ident = entityIsIdent[0]	
							
								filename = createImage(entity, "%s" % (ident), "%s-%s" % (uuid[0], i), toCreate['Entities'][entity]['makeThumbnail'], toCreate['Entities'][entity]['faimsSync'])
								sqlData.append("INSERT INTO aentvalue (uuid, attributeid, valuetimestamp, userid, measure, certainty, freetext, deleted) values( %s, %s, '%s', %s, '%s', '%s', '%s', %s);" % (uuid[0], attributeid, aentvaluetimestamp, useridList[0][0], filename, certainty, annotation, deleted))
					if self['faims_attribute_name'] in toCreate['Entities'][entity]['videoAttribute']:
						for i in range(0,random.randint(toCreate['Entities'][entity]['averageFilesPerRecord']-toCreate['Entities'][entity]['fileVariationPerRecord'],toCreate['Entities'][entity]['averageFilesPerRecord']+toCreate['Entities'][entity]['fileVariationPerRecord'])):
							entityIsIdent = con.cursor().execute("select group_concat(measure) from latestNonDeletedArchEntIdentifiers where uuid = %s group by uuid;" % (uuid[0])).fetchone()
							if entityIsIdent:
								ident = entityIsIdent[0]	
							
								filename = createMP4("%s" % (ident), "%s-%s" % (uuid[0], i), toCreate['Entities'][entity]['makeThumbnail'], toCreate['Entities'][entity]['faimsSync'])
								sqlData.append("INSERT INTO aentvalue (uuid, attributeid, valuetimestamp, userid, measure, certainty, freetext, deleted) values( %s, %s, '%s', %s, '%s', '%s', '%s', %s);" % (uuid[0], attributeid, aentvaluetimestamp, useridList[0][0], filename, certainty, annotation, deleted))
					if self['faims_attribute_name'] in toCreate['Entities'][entity]['fileAttribute']:
						for i in range(0,random.randint(toCreate['Entities'][entity]['averageFilesPerRecord']-toCreate['Entities'][entity]['fileVariationPerRecord'],toCreate['Entities'][entity]['averageFilesPerRecord']+toCreate['Entities'][entity]['fileVariationPerRecord'])):
							entityIsIdent = con.cursor().execute("select group_concat(measure) from latestNonDeletedArchEntIdentifiers where uuid = %s group by uuid;" % (uuid[0])).fetchone()
							if entityIsIdent:
								ident = entityIsIdent[0]	
							
								filename = createPDF("%s" % (ident), "%s-%s" % (uuid[0], i), toCreate['Entities'][entity]['faimsSync'])
								sqlData.append("INSERT INTO aentvalue (uuid, attributeid, valuetimestamp, userid, measure, certainty, freetext, deleted) values( %s, %s, '%s', %s, '%s', '%s', '%s', %s);" % (uuid[0], attributeid, aentvaluetimestamp, useridList[0][0], filename, certainty, annotation, deleted))
					if self['faims_attribute_name'] in toCreate['Entities'][entity]['audioAttribute']:
						for i in range(0,random.randint(toCreate['Entities'][entity]['averageFilesPerRecord']-toCreate['Entities'][entity]['fileVariationPerRecord'],toCreate['Entities'][entity]['averageFilesPerRecord']+toCreate['Entities'][entity]['fileVariationPerRecord'])):
							entityIsIdent = con.cursor().execute("select group_concat(measure) from latestNonDeletedArchEntIdentifiers where uuid = %s group by uuid;" % (uuid[0])).fetchone()
							if entityIsIdent:
								ident = entityIsIdent[0]	
							
								filename = createMP3("%s" % (ident), "%s-%s" % (uuid[0], i), toCreate['Entities'][entity]['faimsSync'])
								sqlData.append("INSERT INTO aentvalue (uuid, attributeid, valuetimestamp, userid, measure, certainty, freetext, deleted) values( %s, %s, '%s', %s, '%s', '%s', '%s', %s);" % (uuid[0], attributeid, aentvaluetimestamp, useridList[0][0], filename, certainty, annotation, deleted))
		sys.stdout.write("%02f%%\n" %((numElement*1.0/numTabgroups*1.0)*100) )





# print "\n".join(sqlData)



# for foo in con.cursor().execute('select * from rtimestamp;'):
# 	print foo

print "Batch archent inserts"

con.cursor().executescript("\n".join(sqlData))


relnSql = []
print "Batch relationships"
for reln in toCreate['Relns']:
	relnAttr = toCreate['Relns'][reln]
	print "making %s \n\t%s" % (reln, relnAttr)
	relntypeid =aenttypequery.execute('select relntypeid from relntype where relntypename = ?', [reln]).fetchone()[0]
	participatesVerbParent = 'null'
	participatesVerbChild  = 'null'
	if relnAttr['useParticipateVerbs']:
		participatesVerbParent, participatesVerbChild = con.cursor().execute('select parent, child from relntype where relntypename = ?', [reln]).fetchone()
	childUUIDlist = con.cursor().execute('select uuid from latestnondeletedarchent join aenttype using (aenttypeid) where aenttypename = ?', [relnAttr['child']]).fetchall()
	for idx, uuid in enumerate(con.cursor().execute('''select distinct uuid from archentity join aenttype using (aenttypeid) where aenttypename = ?;''', [relnAttr['parent']])):
		for i in range(0,random.randint(relnAttr['avgAmountPerParent']-relnAttr['variationPerRecord'],relnAttr['avgAmountPerParent']+relnAttr['variationPerRecord'] )):
			relationshipid = con.cursor().execute('select makeuuid(userid, epoch), timestamp, userid from rtimestamp, user order by random() limit 1;').fetchone()
			deleted = "'true'" if random.random() <= toCreate['Relns'][reln]['deletedRate'] else "null" 
			relnSql.append("INSERT INTO relationship(RelationshipID, RelnTimestamp,deleted, UserID, RelnTypeID) values (%s, '%s', %s, %s, %s);" % (relationshipid[0], relationshipid[1], deleted, relationshipid[2], relntypeid))			
			relnSql.append("INSERT INTO aentreln(uuid, relationshipid, userid, aentrelntimestamp, participatesverb, deleted) values(%s, %s, %s, '%s', '%s', %s);" % (uuid[0], relationshipid[0], relationshipid[2], relationshipid[1], participatesVerbParent, deleted))
			random.shuffle(childUUIDlist)
			relnSql.append("INSERT INTO aentreln(uuid, relationshipid, userid, aentrelntimestamp, participatesverb, deleted) values(%s, %s, %s, '%s', '%s', %s);" % (childUUIDlist[0][0], relationshipid[0], relationshipid[2], relationshipid[1], participatesVerbChild, deleted))
#print '\n'.join(relnSql)
print "Relationship inserts"
con.cursor().executescript("\n".join(relnSql))
  
# for foo in con.cursor().execute('select parent.measure, participatesverb, child.measure from (select uuid, relationshipid, measure, participatesverb from latestNonDeletedArchEntIdentifiers join latestnondeletedaentreln using (uuid)) parent join (select uuid, relationshipid, measure from latestNonDeletedArchEntIdentifiers join latestnondeletedaentreln using (uuid)) child using (relationshipid) where parent.uuid != child.uuid'):
#	print foo



# for foo in con.cursor().execute('select uuid, attributename, measure, certainty, freetext, vocabname from latestnondeletedaentvalue join attributekey using (attributeid) left outer join vocabulary using (vocabid) order by uuid;'):
# 	print foo



	# print element.getparent().getparent().values()


print "compressing"	

fileSet = {}
rootDir = '.'
for dir_, _, files in os.walk(rootDir):
    for fileName in files:
        relDir = os.path.relpath(dir_, rootDir)
        relFile = os.path.join(relDir, fileName)
        fileSet[relFile] = relFile

def md5sum(filename):

	return (filename.replace("./",""), hashfile(open(filename, 'rb'), hashlib.md5()))

def hashfile(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest()



print "done"
hashsum = open('hash_sum', 'w')
hashsum.write(json.dumps(dict(map(md5sum, fileSet))))
hashsum.close()




def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:bz2") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

make_tarfile("../performanceTest.tar.bz2", "../module")