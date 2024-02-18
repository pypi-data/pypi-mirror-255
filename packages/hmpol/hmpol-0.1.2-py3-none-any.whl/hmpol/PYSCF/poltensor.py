"""
Author: Anoop Ajaya Kumar Nair
Date: 2023-10-24
Description: Code calculates:
    - Dipole Quadrupole polarizability tensor
    - Quadrupole Quadrupole polarizability tensor

Contact Details:
- Email: mailanoopanair@gmail.com
- Company: University of Iceland
- Job Title: Doctoral researcher
"""

from pyscf import qmmm, scf
from qdist import Vi, Vij
from ase.units import Bohr, Ha
import numpy as np
from momtensor import Quadrupole



# def calc_Pertb_DP(mol_system, 
#                   mol_COM, 
#                   mol_xc_func, 
#                   box_dim, 
#                   field_component, 
#                   field_strength):

#     charge_postions, charge_mag = Vij(mol_COM,
#                                       box_dim, 
#                                       field_strength,
#                                       field_component)
    
#     mf = qmmm.mm_charge(scf.RKS(mol_system), 
#                         charge_postions, 
#                         charge_mag,
#                         unit='AU')
#     mf.xc = mol_xc_func
#     mf.kernel()
#     dp_mom = mf.dip_moment()
#     return dp_mom


# def calc_Pertb_QP(mol_system, 
#                   mol_COM, 
#                   mol_xc_func, 
#                   box_dim, 
#                   field_component, 
#                   field_strength):

#     charge_postions, charge_mag =Vi(mol_COM,
#                                     box_dim, 
#                                     field_strength,
#                                     field_component)
    
#     mf = qmmm.mm_charge(scf.RKS(mol_system), 
#                         charge_postions, 
#                         charge_mag,
#                         unit='AU')
#     mf.xc = mol_xc_func
#     mf.kernel()
#     qp_mom = Quadrupole(mol_system,mf)
#     return qp_mom





# def calc_FFPertb_Qpole(mol_system, 
#                        mol_COM, 
#                        mol_xc_func, 
#                        box_dim, 
#                        field_component, 
#                        field_strength):
#     charge_postions, charge_mag = Vij(mol_COM,
#                                         box_dim, 
#                                         field_strength,
#                                         field_component)
#     mf = qmmm.mm_charge(scf.RKS(mol_system), 
#                         charge_postions, 
#                         charge_mag,
#                         unit='AU')
#     mf.xc = mol_xc_func
#     mf.kernel()
#     qp_mom = Quadrupole(mol_system,mf)
#     return qp_mom


def calculate_pert_moments( sysdef,
                            sysdef_com,
                            sysdef_box_dim,
                            qc_method,
                            qc_xc_func, 
                            pert_strength,
                            pert_direction,
                            pert_type):
    
    
    charge_postions, charge_mag = pert_type(sysdef_com,
                                            sysdef_box_dim, 
                                            pert_strength,
                                            pert_direction)
    
    mf = qmmm.mm_charge(qc_method(sysdef), 
                        charge_postions, 
                        charge_mag,
                        unit='AU')
    mf.xc = qc_xc_func
    mf.kernel()

    dp_mom = mf.dip_moment()
    qp_mom = Quadrupole(sysdef,mf)


    return dp_mom, qp_mom

    # if pert_direction in ["x","y","z"]:
    #     dp_mom = mf.dip_moment()
    #     return dp_mom
    
    # if pert_direction in ["xx","xy","xz","yy","yz","zz"]:
    #     qp_mom = Quadrupole(sysdef,mf)
    #     return qp_mom
    
    # if pert_strength == 0.0:
    #     dp_mom = mf.dip_moment()
    #     qp_mom = Quadrupole(sysdef,mf)
    #     return dp_mom, qp_mom




class Pols:

    def __init__(   self,
                    mol_struct,
                    mol_system, 
                    mol_xc_func = "pbe",
                    box_dim = 14,
                    field_strength_F = 0.486/Ha*Bohr,
                    field_strength_FF = 0.0486/Ha*Bohr*Bohr,
                    irrep=False):

        self.mol_struct             = mol_struct
        self.sysdef                 = mol_system
        self.sysdef_com             = self.mol_struct.get_center_of_mass()
        self.sysdef_box_dim         = box_dim

        self.qc_method              = scf.RKS
        self.qc_xc_func             = mol_xc_func

        self.field_strength         = field_strength_F
        self.field_direction_x      = 'x'
        self.field_direction_y      = 'y'
        self.field_direction_z      = 'z'

        self.field_grad_strength        = field_strength_FF
        self.field_grad_direction_xx    = "xx"
        self.field_grad_direction_xy    = "xy"
        self.field_grad_direction_xz    = "xz"
        self.field_grad_direction_yy    = 'yy'
        self.field_grad_direction_yz    = 'yz'
        self.field_grad_direction_zz    = 'zz'

        self.apply_field            = Vi
        self.apply_field_gradient   = Vij
        self.irrep                  = irrep

        self.field_grad_strength_ref        = 0.0
        self.field_grad_direction_ref        = "xx"


        self.CONST_DPtoAU           = 0.393456/(self.field_grad_strength)


        self.moment_field_pert_x      =   calculate_pert_moments(   self.sysdef,
                                                                    self.sysdef_com,
                                                                    self.sysdef_box_dim,
                                                                    self.qc_method,
                                                                    self.qc_xc_func, 
                                                                    self.field_strength,
                                                                    self.field_direction_x,
                                                                    self.apply_field)
        
        self.moment_field_pert_y      =   calculate_pert_moments(   self.sysdef,
                                                                    self.sysdef_com,
                                                                    self.sysdef_box_dim,
                                                                    self.qc_method,
                                                                    self.qc_xc_func, 
                                                                    self.field_strength,
                                                                    self.field_direction_y,
                                                                    self.apply_field)
        
        self.moment_field_pert_z      =   calculate_pert_moments(   self.sysdef,
                                                                    self.sysdef_com,
                                                                    self.sysdef_box_dim,
                                                                    self.qc_method,
                                                                    self.qc_xc_func, 
                                                                    self.field_strength,
                                                                    self.field_direction_z,
                                                                    self.apply_field)
 

        self.moment_field_grad_pert_xx =   calculate_pert_moments(  self.sysdef,
                                                                    self.sysdef_com,
                                                                    self.sysdef_box_dim,
                                                                    self.qc_method,
                                                                    self.qc_xc_func, 
                                                                    self.field_grad_strength,
                                                                    self.field_grad_direction_xx,
                                                                    self.apply_field_gradient) 
        
        self.moment_field_grad_pert_xy =   calculate_pert_moments(  self.sysdef,
                                                                    self.sysdef_com,
                                                                    self.sysdef_box_dim,
                                                                    self.qc_method,
                                                                    self.qc_xc_func, 
                                                                    self.field_grad_strength,
                                                                    self.field_grad_direction_xy,
                                                                    self.apply_field_gradient) 
        
        self.moment_field_grad_pert_xz =   calculate_pert_moments(  self.sysdef,
                                                                    self.sysdef_com,
                                                                    self.sysdef_box_dim,
                                                                    self.qc_method,
                                                                    self.qc_xc_func, 
                                                                    self.field_grad_strength,
                                                                    self.field_grad_direction_xz,
                                                                    self.apply_field_gradient) 
        
        self.moment_field_grad_pert_yy =   calculate_pert_moments(  self.sysdef,
                                                                    self.sysdef_com,
                                                                    self.sysdef_box_dim,
                                                                    self.qc_method,
                                                                    self.qc_xc_func, 
                                                                    self.field_grad_strength,
                                                                    self.field_grad_direction_yy,
                                                                    self.apply_field_gradient) 
        
        self.moment_field_grad_pert_yz =   calculate_pert_moments(  self.sysdef,
                                                                    self.sysdef_com,
                                                                    self.sysdef_box_dim,
                                                                    self.qc_method,
                                                                    self.qc_xc_func, 
                                                                    self.field_grad_strength,
                                                                    self.field_grad_direction_yz,
                                                                    self.apply_field_gradient) 
        
        self.moment_field_grad_pert_zz =   calculate_pert_moments(  self.sysdef,
                                                                    self.sysdef_com,
                                                                    self.sysdef_box_dim,
                                                                    self.qc_method,
                                                                    self.qc_xc_func, 
                                                                    self.field_grad_strength,
                                                                    self.field_grad_direction_zz,
                                                                    self.apply_field_gradient) 
        
        self.moment_ref = calculate_pert_moments(   self.sysdef,
                                                    self.sysdef_com,
                                                    self.sysdef_box_dim,
                                                    self.qc_method,
                                                    self.qc_xc_func, 
                                                    self.field_grad_strength_ref,
                                                    self.field_grad_direction_ref,
                                                    self.apply_field_gradient) 



    def calc_dd_pol(self):

        d_0, q_0 = self.moment_ref
        d_x, q_x = self.moment_field_pert_x 
        d_y, q_y = self.moment_field_pert_y 
        d_z, q_z = self.moment_field_pert_z 

        alp_i_x = (d_x - d_0)/self.field_strength
        alp_i_y = (d_y - d_0)/self.field_strength
        alp_i_z = (d_z - d_0)/self.field_strength

        self.alp_ij_IRREP                = np.zeros((6))
        self.alp_ij_IRREP[0]  = alp_i_x[0]
        self.alp_ij_IRREP[1]  = alp_i_x[1]
        self.alp_ij_IRREP[2]  = alp_i_x[2]
        self.alp_ij_IRREP[3]  = alp_i_y[1]
        self.alp_ij_IRREP[4]  = alp_i_y[2]
        self.alp_ij_IRREP[5]  = alp_i_z[2] 

        self.alp_ij = np.zeros((3,3))
        self.alp_ij[:,0] = alp_i_x
        self.alp_ij[:,1] = alp_i_y
        self.alp_ij[:,2] = alp_i_z



        if self.irrep == True:
            np.save("H2O_mono_alpIJ_Trrep.npy",np.round(-self.alp_ij_IRREP,4))
            return np.round(-self.alp_ij_IRREP,4)
        else:
            np.save("H2O_mono_alpIJ.npy",np.round(-self.alp_ij,4))
            return np.round(-self.alp_ij,4)

    def calc_dq_pol(self):

        d_0, q_0 = self.moment_ref
        

        d_x, q_x = self.moment_field_pert_x 
        d_y, q_y = self.moment_field_pert_y 
        d_z, q_z = self.moment_field_pert_z 


        d_xx, q_xx = self.moment_field_grad_pert_xx 
        d_xy, q_xy = self.moment_field_grad_pert_xy 
        d_xz, q_xz = self.moment_field_grad_pert_xz 
        d_yy, q_yy = self.moment_field_grad_pert_yy 
        d_yz, q_yz = self.moment_field_grad_pert_yz 
        d_zz, q_zz = self.moment_field_grad_pert_zz

        A_i_xx = (d_xx - d_yy)*self.CONST_DPtoAU
        A_i_yy = (d_yy - d_zz)*self.CONST_DPtoAU
        A_i_zz = (d_zz - d_xx)*self.CONST_DPtoAU
        A_ij_x = (q_x - q_0)/self.field_strength
        A_ij_y = (q_y - q_0)/self.field_strength
        A_ij_z = (q_z - q_0)/self.field_strength


        self.A_ijk_IRREP                = np.zeros((18))

        # Irreducible representation
        self.A_ijk_IRREP[[0,6,12]]      = A_i_xx
        self.A_ijk_IRREP[[3,9,15]]      = A_i_yy
        self.A_ijk_IRREP[[5,11,17]]     = A_i_zz
        self.A_ijk_IRREP[[1,2,4]]       = A_ij_x[[0,0,1],[1,2,2]]
        self.A_ijk_IRREP[[7,8,10]]      = A_ij_y[[0,0,1],[1,2,2]]
        self.A_ijk_IRREP[[13,14,16]]    = A_ij_z[[0,0,1],[1,2,2]]



        # Full matrix representation
        self.A_ijk = np.zeros((3,3,3))
        self.A_ijk[:,0,0] = A_i_xx
        self.A_ijk[:,1,1] = A_i_yy
        self.A_ijk[:,2,2] = A_i_zz
        self.A_ijk[0,[0,0,1],[1,2,2]] = A_ij_x[[0,0,1],[1,2,2]]
        self.A_ijk[1,[0,0,1],[1,2,2]] = A_ij_y[[0,0,1],[1,2,2]]
        self.A_ijk[2,[0,0,1],[1,2,2]] = A_ij_z[[0,0,1],[1,2,2]]
        self.A_ijk[0,[1,2,2],[0,0,1]] = A_ij_x[[0,0,1],[1,2,2]]
        self.A_ijk[1,[1,2,2],[0,0,1]] = A_ij_y[[0,0,1],[1,2,2]]
        self.A_ijk[2,[1,2,2],[0,0,1]] = A_ij_z[[0,0,1],[1,2,2]]

        if self.irrep == True:
            np.save("H2O_mono_AIJK_Trrep.npy",np.round(self.A_ijk_IRREP,4))
            return np.round(self.A_ijk_IRREP,4)
        else:
            np.save("H2O_mono_AIJK.npy",np.round(self.A_ijk,4))
            return np.round(self.A_ijk,4)





    def calc_qq_pol(self):

        d_0, q_0 = self.moment_ref

        d_xx, q_xx = self.moment_field_grad_pert_xx 
        d_xy, q_xy = self.moment_field_grad_pert_xy 
        d_xz, q_xz = self.moment_field_grad_pert_xz 
        d_yy, q_yy = self.moment_field_grad_pert_yy 
        d_yz, q_yz = self.moment_field_grad_pert_yz 
        d_zz, q_zz = self.moment_field_grad_pert_zz


        C_ijxx = (q_xx - q_yy)/(3*self.field_grad_strength)
        C_ijyy = (q_yy - q_zz)/(3*self.field_grad_strength)
        C_ijzz = (q_zz - q_xx)/(3*self.field_grad_strength)
        C_ijxy = (q_xy - q_0)/self.field_grad_strength
        C_ijyz = (q_yz - q_0)/self.field_grad_strength
        C_ijxz = (q_xz - q_0)/self.field_grad_strength
        C_xyxy = C_ijxy[0,1]/2.0
        C_xyyz = C_ijyz[0,1]
        C_xzyz = C_ijyz[0,2]
        C_yzyz = C_ijyz[1,2]/2.0
        C_xyxz = C_ijxz[0,1]
        C_xzxz = C_ijxz[0,2]/2.0
        C_ijxx   = (q_xx - q_0)/self.field_grad_strength
        C_ijyy   = (q_yy - q_0)/self.field_grad_strength
        C_ijxxyy = (q_xx - q_yy)/self.field_grad_strength
        C_xxxx =  -C_ijxxyy[0,0]/3.0
        C_xxyy =  -C_ijxxyy[1,1]/3.0
        C_xxzz =  -C_ijxxyy[2,2]/3.0
        C_yyyy =  +C_xxyy - C_ijyy[1,1]
        C_yyzz =  +C_xxzz - C_ijyy[2,2]
        C_zzzz =  +C_xxzz + C_ijxx[2,2]

        # Irreducible representation
        self.C_ijkl_IRREP = np.zeros(21)
        self.C_ijkl_IRREP[0]   = round(float(C_xxxx),5)
        self.C_ijkl_IRREP[1]   = round(float(C_ijxx[0,1]),5)
        self.C_ijkl_IRREP[2]   = round(float(C_ijxx[0,2]),5)
        self.C_ijkl_IRREP[3]   = round(float(C_xxyy),5)
        self.C_ijkl_IRREP[4]   = round(float(C_ijxx[1,2]),5)
        self.C_ijkl_IRREP[5]   = round(float(C_xxzz),5)
        self.C_ijkl_IRREP[6]   = round(float(C_xyxy),5)
        self.C_ijkl_IRREP[7]   = round(float(C_xyxz),5)
        self.C_ijkl_IRREP[8]   = round(float(C_ijyy[0,1]),5)
        self.C_ijkl_IRREP[9]   = round(float(C_xyyz),5)
        self.C_ijkl_IRREP[10]  = round(float(C_ijzz[0,1]),5)
        self.C_ijkl_IRREP[11]  = round(float(C_xzxz),5)
        self.C_ijkl_IRREP[12]  = round(float(C_ijyy[0,2]),5)
        self.C_ijkl_IRREP[13]  = round(float(C_xzyz),5)
        self.C_ijkl_IRREP[14]  = round(float(C_ijzz[0,2]),5)
        self.C_ijkl_IRREP[15]  = round(float(C_yyyy),5)
        self.C_ijkl_IRREP[16]  = round(float(C_ijyy[1,2]),5)
        self.C_ijkl_IRREP[17]  = round(float(C_yyzz),5)
        self.C_ijkl_IRREP[18]  = round(float(C_yzyz),5)
        self.C_ijkl_IRREP[19]  = round(float(C_ijzz[1,2]),5)
        self.C_ijkl_IRREP[20]  = round(float(C_zzzz),5)

 
        self.C_ijkl = np.zeros((3,3,3,3))

        self.C_ijkl[0,0,0,0] = self.C_ijkl_IRREP[0]
        self.C_ijkl[[0,1,0,0],
                    [1,0,0,0],
                    [0,0,0,1],
                    [0,0,1,0]] = self.C_ijkl_IRREP[1]
        self.C_ijkl[[0,2,0,0],
                    [2,0,0,0],
                    [0,0,0,2],
                    [0,0,2,0]] = self.C_ijkl_IRREP[2]
        self.C_ijkl[[1,0],
                    [1,0],
                    [0,1],
                    [0,1]] = self.C_ijkl_IRREP[3]
        self.C_ijkl[[1,2,0,0],
                    [2,1,0,0],
                    [0,0,1,2],
                    [0,0,2,1]] = self.C_ijkl_IRREP[4]
        self.C_ijkl[[2,0],
                    [2,0],
                    [0,2],
                    [0,2]] = self.C_ijkl_IRREP[5]
        self.C_ijkl[[0,0,1,1],
                    [1,1,0,0],
                    [0,1,0,1],
                    [1,0,1,0]] = self.C_ijkl_IRREP[6]
        self.C_ijkl[[0,0,2,2,0,1,0,1],
                    [2,2,0,0,1,0,1,0],
                    [0,1,0,1,0,0,2,2],
                    [1,0,1,0,2,2,0,0]] = self.C_ijkl_IRREP[7]
        self.C_ijkl[[1,1,0,1],
                    [1,1,1,0],
                    [0,1,1,1],
                    [1,0,1,1]] = self.C_ijkl_IRREP[8]
        self.C_ijkl[[1,1,2,2,0,1,0,1],
                    [2,2,1,1,1,0,1,0],
                    [0,1,0,1,1,1,2,2],
                    [1,0,1,0,2,2,1,1]] = self.C_ijkl_IRREP[9]
        self.C_ijkl[[2,2,0,1],
                    [2,2,1,0],
                    [0,1,2,2],
                    [1,0,2,2]] = self.C_ijkl_IRREP[10]
        self.C_ijkl[[0,0,2,2],
                    [2,2,0,0],
                    [0,2,0,2],
                    [2,0,2,0]] = self.C_ijkl_IRREP[11]
        self.C_ijkl[[1,1,0,2],
                    [1,1,2,0],
                    [0,2,1,1],
                    [2,0,1,1]] = self.C_ijkl_IRREP[12]
        self.C_ijkl[[1,1,2,2,0,2,0,2],
                    [2,2,1,1,2,0,2,0],
                    [0,2,0,2,1,1,2,2],
                    [2,0,2,0,2,2,1,1]] = self.C_ijkl_IRREP[13]
        self.C_ijkl[[2,2,0,2],
                    [2,2,2,0],
                    [0,2,2,2],
                    [2,0,2,2]] = self.C_ijkl_IRREP[14]
        self.C_ijkl[1,1,1,1] = self.C_ijkl_IRREP[15]
        self.C_ijkl[[1,2,1,1],
                    [2,1,1,1],
                    [1,1,1,2],
                    [1,1,2,1]] = self.C_ijkl_IRREP[16]
        self.C_ijkl[[2,1],
                    [2,1],
                    [1,2],
                    [1,2]] = self.C_ijkl_IRREP[17]
        self.C_ijkl[[1,1,2,2],
                    [2,2,1,1],
                    [1,2,1,2],
                    [2,1,2,1]] = self.C_ijkl_IRREP[18]
        self.C_ijkl[[2,2,1,2],
                    [2,2,2,1],
                    [1,2,2,2],
                    [2,1,2,2]] = self.C_ijkl_IRREP[19]
        self.C_ijkl[2,2,2,2] = self.C_ijkl_IRREP[20]

        if self.irrep == True:
            np.save("H2O_mono_CIJKL_Trrep.npy",np.round(-self.C_ijkl_IRREP,4))
            return np.round(-self.C_ijkl_IRREP,4)
        else:
            np.save("H2O_mono_CIJKL.npy",np.round(-self.C_ijkl,4))
            return np.round(-self.C_ijkl,4)

