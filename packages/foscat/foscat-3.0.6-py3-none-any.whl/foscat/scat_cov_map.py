import foscat.scat_cov as scat
import healpy as hp
class scat_cov_map:
    def __init__(self,p00,s0,s1,s2,s2l,j1,j2,cross=False,backend=None):

        the_scat=scat(P00, C01, C11, s1=S1, c10=C10,backend=self.backend)
        the_scat.set_bk_type('SCAT_COV_MAP')
        return the_scat
    
    def fill(self,im,nullval=hp.UNSEEN):
        return self.fill_healpy(im,nullval=nullval)

class funct(scat.funct):
    def __init__(self, *args, **kwargs):
        # Impose return_data=True pour la classe scat
        super(funct, self).__init__(return_data=True, *args, **kwargs)
