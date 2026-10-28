"""Small client for the editor's HTTP MCP endpoint."""
import requests, json, sys

class Client:
    def __init__(self):
        self.session=requests.Session(); self.url='http://127.0.0.1:8000/mcp'; self.i=0
        r=self.rpc('initialize',{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'codex','version':'1'}})
        self.session.headers['Mcp-Session-Id']=r.headers['Mcp-Session-Id']
    def rpc(self,method,params):
        self.i+=1
        r=self.session.post(self.url,json={'jsonrpc':'2.0','id':self.i,'method':method,'params':params},timeout=60)
        r.raise_for_status(); return r
    def call(self,toolset,tool,args):
        r=self.rpc('tools/call',{'name':'call_tool','arguments':{'toolset_name':toolset,'tool_name':tool,'arguments':args}}).json()
        result=r['result']
        if result.get('isError'): raise RuntimeError(result)
        return result

if __name__=='__main__':
    c=Client(); print(json.dumps(c.call(sys.argv[1],sys.argv[2],json.loads(sys.argv[3]) if len(sys.argv)>3 else {}),ensure_ascii=False))
