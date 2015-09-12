def shorten_url(url): # returns shortened URL
	try:
		post_url = 'https://www.googleapis.com/urlshortener/v1/url'
		postdata = {'longUrl':url}
		headers = {'Content-Type':'application/json'}
		req = urllib2.Request(
			post_url,
			json.dumps(postdata),
			headers
		)
		ret = urllib2.urlopen(req).read()
		return json.loads(ret)['id']
	except:
		return ''

def count_numbers(ds):
	if re.search('[0-9]+', ds) != None:
		return len( (re.search('[0-9]+', ds)).group() )
	else:
		return 0
		
def splitMessage(original_message,l=400,split=','): #splits message into chucnks of maximum length l, separated my most recent character split before length l is reached
	if len(original_message) > l:
		new_message=''
		original_message=original_message.split(split)
		messages_to_send=[]
		c=0
		while len(split.join(original_message)) > l and c < 5:
			c+=1
			while len(new_message) < l:
				last_original_message_array=original_message
				add_to_message=original_message.pop(0)
				last_original_message=new_message
				new_message+=add_to_message+split
			if len(messages_to_send) > 0: last_original_message="(cont'd) "+last_original_message.strip()
			messages_to_send.append(last_original_message.strip())
			original_message=last_original_message_array
			new_message=''
			messages_to_send[-1]=messages_to_send[-1][:-len(split)+1]
		return messages_to_send
	else:
		return [original_message]

def most_recent_play(gid):
	pg=urllib.urlopen("http://espn.go.com/ncf/playbyplay?gameId="+gid).read()
	pg=pg[pg.find('espn.gamepackage.data = ')+len('espn.gamepackage.data = '):]
	pg=pg[:pg.find('}};')+2]
	pg=json.loads(pg)
	try:
		poss=k4v(str(pg['drives']['current']['plays'][0]['end']['team']['id']),db['teams'])
		toret=pg['drives']['current']['plays'][-1]['text']+' (This drive: '+pg['drives']['current']['description']+')'
		return [toret,poss]
	except:
		return ['','']

def gameInfo(gm,color=False,showMr=False,score=True,branked=False,custformat='',supershort=False,newdb=False):
	if not newdb: ourgame=db['games'][gm]
	else: ourgame=newdb[gm]
	if ourgame['status'].lower().count('pm et') != 0 or ourgame['status'].lower().count('am et') != 0: score=False
	t1c=''
	t2c=''
	if color:
		cis=artolower(db['colors'])
		if ourgame['team1'].lower() in cis: 
			t1c=str(cis[ourgame['team1'].lower()][0])+','+str(cis[ourgame['team1'].lower()][1])
		if ourgame['team2'].lower() in cis: 
			t2c=str(cis[ourgame['team2'].lower()][0])+','+str(cis[ourgame['team2'].lower()][1])
	t1s=ourgame['team1']
	t2s=ourgame['team2']
	if supershort: shorts=artolower(db['supershorten'])
	else: shorts=artolower(db['shorten'])
	if t1s.lower() in shorts and shorts[t1s.lower()].strip() != '': t1s=shorts[t1s.lower()]
	if t2s.lower() in shorts and shorts[t2s.lower()].strip() != '': t2s=shorts[t2s.lower()]
	if score:
		t1=t1s+' '+ourgame['team1score']
		t2=t2s+' '+ourgame['team2score']
	else:
		t1=t1s
		t2=t2s
	if len(t1.split()) > 1:
		if t1.split()[1][0]=='(': t1=t1.split()[0]
	if len(t2.split()) > 1:
		if t2.split()[1][0]=='(': t2=t2.split()[0]
	rks=artolower(db['ranks'])
	btgame=False
#	print ourgame['team1'].lower()
	if ourgame['team1'].lower() in rks and rks[ourgame['team1'].lower()] != None:
		t1='('+rks[ourgame['team1'].lower()]+') '+t1
		#print branked
		if branked: btgame=True
	if ourgame['team2'].lower() in rks and rks[ourgame['team2'].lower()] != None:
		t2='('+rks[ourgame['team2'].lower()]+') '+t2
		if branked: btgame=True
	#print btgame
	ntwks=''
	if gm in db['ntwks']:
		if db['ntwks'][gm] != '': ntwks=' - '+db['ntwks'][gm]
	mr=''
	if ourgame['status'].upper().count('FINAL') == 1: ntwks=''
	status=ourgame['status']
	if status.lower().count('am et') != 0 or status.lower().count('pm et') != 0:
		std=status
		stds=std[:std.find(',')]
		std=std[std.find(',')+2:]
		std=std[std.find(' ')+1:]
		std=std[std.find(' ')+1:]
		std=stds+' '+std
		status=std
	status=status.replace(' ET','')+ntwks
	poss=''
	if ourgame['status'].upper().count('FINAL') == 0 and ourgame['status'].upper().count('PM ET') == 0 and ourgame['status'].upper().count('AM ET') == 0 and showMr:
		mrg=most_recent_play(ourgame['gid'])
		poss=mrg[1]
		if showMr: mr=': '+mrg[0]
		if len(mr) < 5: mr=''
	if ourgame['team1']==poss: t1=t1+' (:)'
	elif ourgame['team2']==poss: t2=t2+' (:)'
	if t1c != '': t1=chr(3)+t1c+t1+chr(3)
	if t2c != '': t2=chr(3)+t2c+t2+chr(3)
	nident=' vs. '
	if 'neutral' in ourgame and not ourgame['neutral']: nident=' @ '
	bt=''
	if btgame: bt='\x02'
	stat_to_show=ourgame['status'].strip()
	if supershort and (stat_to_show.count('PM ET') != 0 or stat_to_show.count('AM ET') != 0):
		stat_to_show1=stat_to_show[:stat_to_show.find(',')].strip()
		stat_to_show2=stat_to_show[stat_to_show.find(',')+1:].strip()
		stat_to_show2=stat_to_show2[stat_to_show2.find(' '):].strip()
		stat_to_show2=stat_to_show2[stat_to_show2.find(' '):].strip()
		stat_to_show=stat_to_show1+' '+stat_to_show2
	if custformat != '':	
		return custformat.replace('%BT%',bt.strip()).replace('%T1%',t1.strip()).replace('%T2%',t2.strip()).replace('%NIDENT%',nident.strip()).replace('%MR%',mr.strip()).replace('%STATUS%',stat_to_show.strip()).replace('%NTWKS%',ntwks.strip())
	else: return bt+t1.strip()+nident+t2.strip()+mr.strip()+' '+stat_to_show+' '+ntwks.strip()+bt
#			db['msgqueue'].append([t1+' '+nident+t2.strip()+mr.strip()+' '+ourgame['status']+ntwks,dest,tmtype,'score'])

def abbrev(words,abb,debug=False): # convert abbreviations to full
	con=abb
	for throw,ws in con.iteritems():
		#print words.lower()+'.'+ws[0].lower()+'.'
		if ws[0] != None and words.lower().strip()==ws[0].lower().strip(): words=ws[1]
		#if debug: print words+'.'+ws[0]+'.'+ws[1]+'.'
	return words

def stats(gid):
	soup=BeautifulSoup(urllib.urlopen('http://espn.go.com/college-football/matchup?gameId='+gid).read(),"html5lib")
	teams=soup.findAll('span',{'class':'chartLabel'})
	t1=teams[0].getText()
	t2=teams[1].getText()
	tb=soup.find('article',{'class':'team-stats-list'})
	tb=tb.find('table',{'class':'mod-data'})
	rows=tb.findAll('tr')
	stats=[]
	for row in rows:
		if row['class'][0]!='header':
			cols=row.findAll('td')
			if len(cols) > 2: stats.append(cols[0].contents[0].strip()+': '+t1+' '+cols[1].contents[0].strip()+' '+t2+' '+cols[2].contents[0].strip())
	return ', '.join(stats)

def k4v(v,ar): # return key for value v in array ar
	for a,b in ar.iteritems():
		if b == v:
			return a

def artolower(art): #make all values in array lowercase
	newar={}
	for a,b in art.iteritems(): newar[a.lower()]=b
	return newar
def remove_rank(dstr): # removes ranking from team name
	return re.sub(r'\([0-9)]*\)', '',dstr).strip()
	
def match(w): # find closest team to w
	closestval=1000000
	closests=''
	teams=db['games']
	params=abbrev(w.lower(),db['abbreviations'],True)
	for a,b in teams.iteritems():
		if a != 'lastupdate':
			team1=b['team1'].lower().replace('(','').replace(')','')
			team2=b['team2'].lower().replace('(','').replace(')','')
			tclv1=closest([params,params+' StateZ'],[team1])
			tclv2=closest([params,params+' StateZ'],[team2])
			if tclv1 < closestval:
				closestval=tclv1
				closests=team1
			if tclv2 < closestval:
				closestval=tclv2
				closests=team2
	if closests != '' and closestval < 3:
		return closests
	else:
		return False


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()