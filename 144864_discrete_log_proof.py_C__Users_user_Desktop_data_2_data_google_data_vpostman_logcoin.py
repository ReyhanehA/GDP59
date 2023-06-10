def dlog_know(x,r,p,g,which):
	if which==1:
		return (x+r)%(p-1)
	return r
def dlog_verify(C,res,y,p,g,which):
	if which==1:
		return (pow(g,res,p)==(C*y)%p)
	return (pow(g,res,p) == C)
def proto_exchange_verify(g,p,y,prng,send,recv,thresh):
	while thresh>0:
		send(2)
		which=(prng()%2)
		C=recv()
		send(which)
		res=recv()
		if dlog_verify(C,res,y,p,g,which)==False:
			send(1)
			return False
		thresh-=1
	send(0)
	return True
def proto_exchange_prove(g,p,x,prng,send,recv):
	q=2
	while(q==2):
		q=recv()
		if(q!=2):
			break
		r=prng()
		send(pow(g,r,p))
		which=recv()
		send(dlog_know(x,r,p,g,which))
	return (q==0)
