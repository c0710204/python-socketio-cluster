from src.libs.app.server import app_server
import time
img_list = [
    "/scratch/guxi/googlestreeview_download/image/000/DimBS_bGYVSVQ1teobDOsw.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/dJailiEhu-HSpp9LLh3f0Q.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/DjikukBs3hWWwWrN2r4CEg.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/DjjepcEhpdUbqg6GFSZFHg.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/djnVVJt2jGKClnnVbDRy3Q.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/dniq-925szaR4v20LN1Z5g.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/DNqzV8rJAlSHtABlcPtqIA.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/dSNCKIb9f0397dnhnyDfgw.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/dSPjzzCiOQAS9VibfIZf-A.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/DX1f_6UXESWavjNiQLUvvQ.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/e0nxY0r2DmZkhCNzYgfvRQ.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/E6p40qx_8-9cSi6e_YDx1w.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/E7BXCAFMC0wYrbKrLhFeIg.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/eAbeAkSoEdp6GkOjWk2neQ.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/eAuqEpeR70TfLcPg8rarxg.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/EcTiqZthCUNA3yf_O5Y4bg.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/ehLgJenEj9TK_EM_qAVJuQ.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/EL9qoIfs3lwnfYaxT39iuQ.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/eMoFPt--PwFGVhfQnj-38w.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/EmQ40Zain7Q2OSSeIWZF8A.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/EnerSEO95Nl_xeJ-C7hvMA.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/eOdxmHtalOFVz-A_b3qx6g.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/EpF9QD9wYNL1_7BJVbj6rg.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/Er6evWQnOCQ1PB-en3iNNA.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/ER_BXxuGSbJtRbEV64zj4A.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/EuRKMp7E1eP79TdBUjbbcg.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/EUWsd5w_vkGRjrJs3PkitQ.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/ewYvWFUWUH_kYG64huz2rA.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/EZjPNAIFx1fzMsAftncpXg.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/f2SpnSdmbrY7Ix0Sy4fBeA.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/F3b1i-D3F58tCmOVQi9IIg.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/F3_iWDWqY-E2xLnCTR86lQ.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/-fbCGtg5EBAGi9pqv8ZsuA.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/fbHZzcZLHtHB6a5fSTFkfA.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/fBvPA144oILNQhpjpB5LWw.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/FDFD9iL0rxbD8hD3yZT0tA.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/FegLNfyv75K-E5xHNjWZlw.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/FJJGrSnNIoXpo1pAtitLXQ.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/fnGLApBjjo86cSkCKMj9aQ.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/FnMuOMRJkUuuq2o_hajoNg.jpg",
    "/scratch/guxi/googlestreeview_download/image/000/Fo8bJ_8giSF523Sl81ll4w.jpg",
]

def package(input_path, output_path):
    return {
        "proxy": {
            "host": "star.eecs.oregonstate.edu",
            "username": "guxi",
            "password": "cft6&UJM",
            "port": 22,
        },
        "ssh": {
            "host": "127.0.0.1",
            "username": "guxi",
            "password": "dHtFkI6g",
            "port": 50022,
        },
        "input_path": input_path,
        "output_path": output_path
    }


class pspnet_app_server(app_server):
    def __init__(self,*args):
        app_server.__init__(self,*args)
    def handle_error(self,err,arg):
        pass
    def get_task(self):
        """
        :param args all needed data from server
        """
        global img_list
        if data:
            print(data['input_path'],time.asctime( time.localtime(time.time())  ))
        if len(img_list) > 0:
            img_local = img_list[-1]
            del img_list[-1]
            print("[{1}]sending request : {0} image left".format(len(img_list),time.asctime( time.localtime(time.time()) )))
            return package(img_local, "/scratch/guxi/googlestreeview_download/result/000/")

    def process_result(self,ret):
        """
        :param ret result from client.run
        """
        pass

def handler():
    return pspnet_app_server
def main():
    #dummy
    pass
    #srv=pspnet_app_server()

    #client = mdl_cli.pspnet_app_client()
    #print(srv.process_result(client.run(srv.get_task())))
if __name__ == '__main__':
    main()
