import apps.streetdownloader.pkg.streetview.streetview
class app_client():
    pass
class stv_app_client(app_client):
    def run(self,args):
        """
        :param args all needed data from server
        """


        panoids = streetview.panoids(lat= args['lat'], lon= args['lng'])
        return panoids

def main():
    loc_test=stv_app_client()
    ret=loc_test.run({"lat":-37.83314,"lon": 144.919085})
    print()
if __name__ == '__main__':
    main()
