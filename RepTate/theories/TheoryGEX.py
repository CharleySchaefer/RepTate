# RepTate: Rheology of Entangled Polymers: Toolkit for the Analysis of Theory and Experiments
# --------------------------------------------------------------------------------------------------------
#
# Authors:
#     Jorge Ramirez, jorge.ramirez@upm.es
#     Victor Boudara, victor.boudara@gmail.com
#
# Useful links:
#     http://blogs.upm.es/compsoftmatter/software/reptate/
#     https://github.com/jorge-ramirez-upm/RepTate
#     http://reptate.readthedocs.io
#
# --------------------------------------------------------------------------------------------------------
#
# Copyright (2018): Jorge Ramirez, Victor Boudara, Universidad Politécnica de Madrid, University of Leeds
#
# This file is part of RepTate.
#
# RepTate is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RepTate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RepTate.  If not, see <http://www.gnu.org/licenses/>.
#
# --------------------------------------------------------------------------------------------------------
"""Module TheoryGEX

GEX file for creating a new theory
"""
import numpy as np
from math import gamma
from CmdBase import CmdBase, CmdMode
from Parameter import Parameter, ParameterType, OptType
from Theory import Theory
from QTheory import QTheory
from DataTable import DataTable


class TheoryGEX(CmdBase):
    """[summary]
    
    [description]
    """
    thname = 'GEXTheory'
    description = 'Generalized Exponential Function (GEX)'
    citations = ''

    def __new__(cls, name='ThGEX', parent_dataset=None, axarr=None):
        """[summary]
        
        [description]
        
        Keyword Arguments:
            - name {[type]} -- [description] (default: {'ThGEX'})
            - parent_dataset {[type]} -- [description] (default: {None})
            - ax {[type]} -- [description] (default: {None})
        
        Returns:
            - [type] -- [description]
        """
        return GUITheoryGEX(
            name, parent_dataset,
            axarr) if (CmdBase.mode == CmdMode.GUI) else CLTheoryGEX(
                name, parent_dataset, axarr)


class BaseTheoryGEX:
    """Generalized Exponential Function (GEX) for experimental molecular weight distributions.
    
    * **Function**
        .. math::
            W(M) = W_0 \\frac{b}{M_0 \\Gamma\\left(\\frac{a}{b}\\right)} \\left(\\frac{M}{M_0}\\right)^{a-1} \\exp\\left[ -\\left(\\frac{M}{M_0}\\right)^b \\right]
    
    * **Parameters**
       - :math:`\\log_10(W_0)`: Normalization constant.
       - :math:`\\log_10(M_0)`: .
       - :math:`a`: .
       - :math:`b`: .
    """
    #help_file = ''
    single_file = False  # False if the theory can be applied to multiple files simultaneously

    def __init__(self, name='ThGEX', parent_dataset=None, axarr=None):
        """
        **Constructor**
        
        Keyword Arguments:
            - name {[type]} -- [description] (default: {'ThGEX'})
            - parent_dataset {[type]} -- [description] (default: {None})
            - ax {[type]} -- [description] (default: {None})
        """
        super().__init__(name, parent_dataset, axarr)
        self.function = self.GEX  # main theory function
        self.has_modes = False  # True if the theory has modes
        self.parameters['logW0'] = Parameter(
            name='logW0',
            value=5,
            description='logW0',
            type=ParameterType.real,
            opt_type=OptType.opt)
        self.parameters['logM0'] = Parameter(
            name='logM0',
            value=5,
            description='logM0',
            type=ParameterType.real,
            opt_type=OptType.opt)
        self.parameters['a'] = Parameter(
            name='a',
            value=1,
            description='a',
            type=ParameterType.real,
            opt_type=OptType.opt,
            bracketed=True,
            min_value=0)
        self.parameters['b'] = Parameter(
            name='b',
            value=0.5,
            description='b',
            type=ParameterType.real,
            opt_type=OptType.opt,
            bracketed=True,
            min_value=0)

    def get_modes(self):
        """[summary]
        
        [description]
        
        Returns:
            - [type] -- [description]
        """
        pass

    def set_modes(self):
        """[summary]
        
        [description]
        
        Arguments:

        """
        pass
    
    def destructor(self):
        """[summary]
        
        [description]
        
        Arguments:

        """
        pass

    def GEX(self, f=None):
        """GEX function that returns the square of y
        
        [description]
        
        Keyword Arguments:
            - f {[type]} -- [description] (default: {None})
        
        Returns:
            - [type] -- [description]
        """
        ft = f.data_table
        tt = self.tables[f.file_name_short]
        tt.num_columns = ft.num_columns
        tt.num_rows = ft.num_rows
        W0 = np.power(10.0,self.parameters["logW0"].value)
        M0 = np.power(10.0,self.parameters["logM0"].value)
        a = self.parameters["a"].value
        b = self.parameters["b"].value
        
        tt.data = np.zeros((tt.num_rows, tt.num_columns))
        tt.data[:, 0] = ft.data[:, 0]
        tt.data[:, 1] = W0*b/M0/gamma((a+1)/b)*np.power(tt.data[:, 0]/M0,a)*np.exp(-np.power(tt.data[:, 0]/M0,b))

    def do_error(self, line):
        super().do_error(line)
        if (line == ""):
            self.Qprint("")
            M0 = np.power(10.0,self.parameters["logM0"].value)
            a = self.parameters["a"].value
            b = self.parameters["b"].value
            Mn = M0*gamma((a+1)/b)/gamma(a/b)
            Mw = M0*gamma((a+2)/b)/gamma((a+1)/b)
            Mz = M0*gamma((a+3)/b)/gamma((a+2)/b)
            self.Qprint("Mn = %g"%Mn)
            self.Qprint("Mw = %g"%Mw)
            self.Qprint("Mz = %g"%Mz)
            self.Qprint("D  = %g"%(Mw/Mn))

class CLTheoryGEX(BaseTheoryGEX, Theory):
    """[summary]
    
    [description]
    """

    def __init__(self, name='ThGEX', parent_dataset=None, axarr=None):
        """
        **Constructor**
        
        Keyword Arguments:
            - name {[type]} -- [description] (default: {'ThGEX'})
            - parent_dataset {[type]} -- [description] (default: {None})
            - ax {[type]} -- [description] (default: {None})
        """
        super().__init__(name, parent_dataset, axarr)

    # This class usually stays empty


class GUITheoryGEX(BaseTheoryGEX, QTheory):
    """[summary]
    
    [description]
    """

    def __init__(self, name='ThGEX', parent_dataset=None, axarr=None):
        """
        **Constructor**
        
        Keyword Arguments:
            - name {[type]} -- [description] (default: {'ThGEX'})
            - parent_dataset {[type]} -- [description] (default: {None})
            - ax {[type]} -- [description] (default: {None})
        """
        super().__init__(name, parent_dataset, axarr)

    # add widgets specific to the theory here: