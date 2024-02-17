# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: =CS-Lib= A RO service for registration of Boxes at a site.
#+end_org """

####+BEGIN: b:py3:cs:file/dblockControls :classification "cs-u"
""" #+begin_org
* [[elisp:(org-cycle)][| /Control Parameters Of This File/ |]] :: dblk ctrls classifications=cs-u
#+BEGIN_SRC emacs-lisp
(setq-local b:dblockControls t) ; (setq-local b:dblockControls nil)
(put 'b:dblockControls 'py3:cs:Classification "cs-u") ; one of cs-mu, cs-u, cs-lib, bpf-lib, pyLibPure
#+END_SRC
#+RESULTS:
: cs-u
#+end_org """
####+END:

####+BEGIN: b:prog:file/proclamations :outLevel 1
""" #+begin_org
* *[[elisp:(org-cycle)][| Proclamations |]]* :: Libre-Halaal Software --- Part Of BISOS ---  Poly-COMEEGA Format.
** This is Libre-Halaal Software. © Neda Communications, Inc. Subject to AGPL.
** It is part of BISOS (ByStar Internet Services OS)
** Best read and edited  with Blee in Poly-COMEEGA (Polymode Colaborative Org-Mode Enhance Emacs Generalized Authorship)
#+end_org """
####+END:

####+BEGIN: b:prog:file/particulars :authors ("./inserts/authors-mb.org")
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars |]]* :: Authors, version
** This File: /bisos/git/bxRepos/bisos-pip/siteRegistrars/py3/bisos/siteRegistrars/csSiteRegContainer.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGINNOT: b:py3:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['csSiteRegContainer'], }
csInfo['version'] = '202401192758'
csInfo['status']  = 'inUse'
csInfo['panel'] = "[[../../panels/_nodeBase_/fullUsagePanel-en.org]]"
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]] :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/PyFwrk/bisos-pip/bisos.cs/_nodeBase_/fullUsagePanel-en.org][BISOS CmndSvcs Panel]]   [[elisp:(org-cycle)][| ]]
** TODO Document this module.
** TODO Add sectioning for Invoker and performer.
** Relevant Panels:
** Status: In use with BISOS
** /[[elisp:(org-cycle)][| Planned Improvements |]]/ :
*** TODO complete fileName in particulars.
#+end_org """

####+BEGIN: b:prog:file/orgTopControls :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Controls |]] :: [[elisp:(delete-other-windows)][(1)]] | [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[file:Panel.org][Panel]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
** /Version Control/ ::  [[elisp:(call-interactively (quote cvs-update))][cvs-update]]  [[elisp:(vc-update)][vc-update]] | [[elisp:(bx:org:agenda:this-file-otherWin)][Agenda-List]]  [[elisp:(bx:org:todo:this-file-otherWin)][ToDo-List]]

#+end_org """
####+END:

####+BEGIN: b:py3:file/workbench :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Workbench |]] :: [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pyclbr %s" (bx:buf-fname))))][pyclbr]] || [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pydoc ./%s" (bx:buf-fname))))][pydoc]] || [[elisp:(python-check (format "/bisos/pipx/bin/pyflakes %s" (bx:buf-fname)))][pyflakes]] | [[elisp:(python-check (format "/bisos/pipx/bin/pychecker %s" (bx:buf-fname))))][pychecker (executes)]] | [[elisp:(python-check (format "/bisos/pipx/bin/pycodestyle %s" (bx:buf-fname))))][pycodestyle]] | [[elisp:(python-check (format "/bisos/pipx/bin/flake8 %s" (bx:buf-fname))))][flake8]] | [[elisp:(python-check (format "/bisos/pipx/bin/pylint %s" (bx:buf-fname))))][pylint]]  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:orgItem/basic :type "=PyImports= " :title "*Py Library IMPORTS*" :comment "-- with classification based framework/imports"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =PyImports=  [[elisp:(outline-show-subtree+toggle)][||]] *Py Library IMPORTS* -- with classification based framework/imports  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:framework/imports :basedOn "classification"
""" #+begin_org
** Imports Based On Classification=cs-u
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io
from bisos.common import csParam

import collections
####+END:


from bisos.siteRegistrars import siteRegPortNu
from bisos.siteRegistrars import invSiteRegContainerConf

import pwd
import pathlib
import ast

import enum

####+BEGIN: b:py3:cs:orgItem/section :title "Common Parameters Specification" :comment "based on cs.param.CmndParamDict -- As expected from CSU-s"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Common Parameters Specification* based on cs.param.CmndParamDict -- As expected from CSU-s  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "commonParamsSpecify" :comment "~CSU Specification~" :funcType "ParSpc" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-ParSpc [[elisp:(outline-show-subtree+toggle)][||]] /commonParamsSpecify/  ~CSU Specification~  [[elisp:(org-cycle)][| ]]
#+end_org """
def commonParamsSpecify(
####+END:
        csParams: cs.param.CmndParamDict,
) -> None:

    csParams.parDictAdd(
        parName='containerNu',
        parDescription="One of: LinuxU, Server",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--containerNu',
    )
    csParams.parDictAdd(
        parName='model',
        parDescription="One of: Host, Pure, Guest",
        parDataType=None,
        #parDefault='ParOne',
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--model',
    )
    csParams.parDictAdd(
        parName='abode',
        parDescription="One of: Shield, Internet",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--abode',
    )
    csParams.parDictAdd(
        parName='purpose',
        parDescription="One of: LinuxU, Server",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--purpose',
    )
    csParams.parDictAdd(
        parName='boxNu',
        parDescription="One of: LinuxU, Server",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--boxNu',
    )



####+BEGIN: b:py3:cs:orgItem/section :title "CSU-Lib Executions" :comment "-- cs.invOutcomeReportControl"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CSU-Lib Executions* -- cs.invOutcomeReportControl  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

perfName = "siteRegistrar"

roSiteRegistrarSapPath = cs.ro.SapBase_FPs.perfNameToRoSapPath(perfName)  # static method

cs.invOutcomeReportControl(cmnd=True, ro=True)


####+BEGIN: bx:dblock:python:section :title "Enumerations"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Enumerations*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:

####+BEGIN: bx:dblock:python:enum :enumName "Models" :comment "Host|Pure|Virt"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Enum       [[elisp:(outline-show-subtree+toggle)][||]] /Models/ =host|pure|virt=  [[elisp:(org-cycle)][| ]]
#+end_org """
@enum.unique
class Models(enum.Enum):
####+END:

    Host = 'H'
    Pure = 'P'
    Virt = 'V'

####+BEGIN: bx:dblock:python:enum :enumName "Abodes" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Enum       [[elisp:(outline-show-subtree+toggle)][||]] /Abodes/  [[elisp:(org-cycle)][| ]]
#+end_org """
@enum.unique
class Abodes(enum.Enum):
####+END:
    Mobile = 'M'  # Old
    Rim_outer = 'Ro' # New

    Shield = 'S'  # Old
    Rim_inner = 'Ri' # New

    Perim = 'Perim'  # Old
    Rim_exposed = 'Re' # New

    Internet  = 'I'  # Old
    Svc = 'Se' # New  # Service Exposed Ring
    Svc_interior = 'Si'  # DMZ for Ring # Service

    Auto = 'A'  #  DHCP  Randomly Assigned

# Abodes('M').name  # withInitialGetAbode

####+BEGIN: bx:dblock:python:enum :enumName "Purposes" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Enum       [[elisp:(outline-show-subtree+toggle)][||]] /Purposes/  [[elisp:(org-cycle)][| ]]
#+end_org """
@enum.unique
class Purposes(enum.Enum):
####+END:
    LinuxU = 'L'  # User Environment
    AndroidU = 'A'
    ChromeVmU = 'C'

    Server = 'S'

    Devel  = 'D'

    Generic = 'G'



####+BEGIN: bx:dblock:python:enum :enumName "Distros" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Enum       [[elisp:(outline-show-subtree+toggle)][||]] /Distros/  [[elisp:(org-cycle)][| ]]
#+end_org """
@enum.unique
class Distros(enum.Enum):
####+END:
    deb10 = 'deb10'
    deb11 = 'deb11'
    deb12 = 'deb12'

    ub2004 = 'ub2004'


# if hasattr(Color, input_var):
    # print('Everything is fine and dandy.')
    #

# values = [member.value for member in Sizes]
# print(values)  # 👉️ [1, 2, 3]

# names = [member.name for member in Sizes]
# print(names)  # 👉️ ['SMALL', 'MEDIUM', 'LARGE']

####+BEGIN: b:py3:cs:orgItem/section :title "Performer Modules Import" :comment "-- After Common Definitions"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Performer Modules Import* -- After Common Definitions  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

from bisos.siteRegistrars import perfSiteRegContainer

####+BEGIN: b:py3:cs:orgItem/section :title "CSU-Lib Examples" :comment "-- Providing examples_csu"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CSU-Lib Examples* -- Providing examples_csu  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "examples_csu" :comment "~CSU Specification~" :funcType "eType" :retType "" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-eType  [[elisp:(outline-show-subtree+toggle)][||]] /examples_csu/  ~CSU Specification~ deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def examples_csu(
####+END:
        sectionTitle: typing.AnyStr = '',
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr* |]] Examples of Service Access Instance Commands.
    #+end_org """

    # def cpsInit(): return collections.OrderedDict()
    # def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'

    cmndOutcome = b.op.Outcome()

    od = collections.OrderedDict
    cmnd = cs.examples.cmndEnter

    perfName = 'localhost'

    thisModel = 'Pure'
    thisAbode = 'Mobile'
    thisPurpose = 'LinuxU'
    thisBoxNu = 'box1014'
    thisContainerNu = '1099'

    unitsPars = collections.OrderedDict([('model', thisModel), ('abode', thisAbode), ('purpose', thisPurpose)])
    unitBasePars = collections.OrderedDict([('model', thisModel), ('abode', thisAbode), ('purpose', thisPurpose), ('containerNu', thisContainerNu)])
    createPars = collections.OrderedDict([('model', thisModel), ('abode', thisAbode), ('purpose', thisPurpose), ('containerNu', thisContainerNu), ('boxNu', thisBoxNu)])

    ro_unitsPars = cs.examples.perfNameParsInsert(unitsPars, perfName)
    ro_unitBasePars = cs.examples.perfNameParsInsert(unitBasePars, perfName)
    ro_createPars = cs.examples.perfNameParsInsert(createPars, perfName)


    cs.examples.menuSection('*RO Service Commands*')



    if sectionTitle == 'default': cs.examples.menuChapter('*Remote Operations -- Invoker and Performer Management*')

    cmnd('reg_sapCreate')

    print(f"""csRo-manage.cs --perfName="siteRegistrar" --rosmu="csSiteRegContainer.cs"  -i ro_fps list""")
    print(f"""csSiteRegContainer.cs --perfName="siteRegistrar" -i csPerformer  & # in background Start rpyc CS Service""")

    if sectionTitle == 'default': cs.examples.menuChapter('*Registrar Svc Commands -- perfName=siteRegistrar*')

    cmnd('reg_container_add', pars=unitBasePars)
    cmnd('reg_container_read', pars=unitBasePars)
    cmnd('reg_container_update', pars=createPars)
    cmnd('reg_container_delete', pars=unitBasePars)
    cmnd('reg_container_find', pars=unitsPars, args=f"boxId {thisBoxNu}")
    cmnd('reg_container_list', pars=unitsPars)


####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Invoke Service Commands At Site Registrar" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Invoke Service Commands At Site Registrar_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reg_sapCreate" :ro "noCli" :comment "" :parsMand "" :parsOpt "rosmuControl" :argsMin 0 :argsMax 0
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reg_sapCreate>>  =verify= parsOpt=rosmuControl ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class reg_sapCreate(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'rosmuControl', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}
    rtInvConstraints = cs.rtInvoker.RtInvoker.new_noRo() # NO RO From CLI

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             rosmuControl: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        callParamsDict = {'rosmuControl': rosmuControl, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        rosmuControl = csParam.mappedValue('rosmuControl', rosmuControl)
####+END:
        """\
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Creates path for ro_sap and updates FPs
        """
        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  csSiteRegContainer.cs -i reg_sapCreate
#+end_src
#+RESULTS:
#+begin_example

FileParam.writeTo path=/bisos/var/cs/ro/sap/csSiteRegContainer.cs/siteRegistrar/rpyc/default/perfIpAddr/value value=192.168.0.90
FileParam.writeTo path=/bisos/var/cs/ro/sap/csSiteRegContainer.cs/siteRegistrar/rpyc/default/perfPortNu/value value=22222001
FileParam.writeTo path=/bisos/var/cs/ro/sap/csSiteRegContainer.cs/siteRegistrar/rpyc/default/accessControl/value value=placeholder
FileParam.writeTo path=/bisos/var/cs/ro/sap/csSiteRegContainer.cs/siteRegistrar/rpyc/default/perfName/value value=siteRegistrar
FileParam.writeTo path=/bisos/var/cs/ro/sap/csSiteRegContainer.cs/siteRegistrar/rpyc/default/perfModel/value value=rpyc
FileParam.writeTo path=/bisos/var/cs/ro/sap/csSiteRegContainer.cs/siteRegistrar/rpyc/default/rosmu/value value=csSiteRegContainer.cs
FileParam.writeTo path=/bisos/var/cs/ro/sap/csSiteRegContainer.cs/siteRegistrar/rpyc/default/rosmuSel/value value=default
FileParam.writeTo path=/bisos/var/cs/ro/sap/csSiteRegContainer.cs/siteRegistrar/rpyc/default/rosmuControl/value value=bisos
/bisos/var/cs/ro/sap/csSiteRegContainer.cs/siteRegistrar/rpyc/default
#+end_example
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        rosmu = cs.G.icmMyName()
        perfModel = "rpyc"

        if rosmuControl:
            perfName = "exampleRegistrar"
            rosmuSel = 'default'  #  A file path to
            perfIpAddr = "localhost"
        else:
            perfName = "siteRegistrar"
            rosmuSel = "default"
            rosmuControl = 'bisos'

            confFps = invSiteRegContainerConf.RegContainerInvConf_FPs()
            ipAddrs_fp =  confFps.fps_getParam('regContainerPerfAddrs')
            ipAddrStr = ipAddrs_fp.parValueGet()
            #print(ipAddrStr)
            ipAddrs = ast.literal_eval(ipAddrStr)
            perfIpAddr = ipAddrs[0]


        if (perfPortList := siteRegPortNu.portNuOf().cmnd(
                rtInv=cs.RtInvoker.new_py(),
                cmndOutcome=cmndOutcome,
                argsList=['csSiteRegContainer']
        ).results) == None : return(b_io.eh.badOutcome(cmndOutcome))

        perfPortNu = perfPortList[0]

        sapBaseFps = b.pattern.sameInstance(cs.ro.SapBase_FPs, rosmu=rosmu, perfName=perfName, perfModel=perfModel, rosmuSel=rosmuSel)

        sapBaseFps.fps_setParam('perfIpAddr', perfIpAddr)
        sapBaseFps.fps_setParam('perfPortNu', perfPortNu)
        sapBaseFps.fps_setParam('accessControl', "placeholder")
        sapBaseFps.fps_setParam('perfName', perfName)
        sapBaseFps.fps_setParam('perfModel', perfModel)
        sapBaseFps.fps_setParam('rosmu', rosmu)
        sapBaseFps.fps_setParam('rosmuSel', rosmuSel)
        sapBaseFps.fps_setParam('rosmuControl', rosmuControl)

        sapPath = sapBaseFps.basePath_obtain()

        return cmndOutcome.set(opResults=sapPath,)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reg_container_add" :comment "" :extent "verify" :ro "cli" :parsMand "model abode purpose" :parsOpt "boxNu" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reg_container_add>>  =verify= parsMand=model abode purpose parsOpt=boxNu ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class reg_container_add(cs.Cmnd):
    cmndParamsMandatory = [ 'model', 'abode', 'purpose', ]
    cmndParamsOptional = [ 'boxNu', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             model: typing.Optional[str]=None,  # Cs Mandatory Param
             abode: typing.Optional[str]=None,  # Cs Mandatory Param
             purpose: typing.Optional[str]=None,  # Cs Mandatory Param
             boxNu: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, 'boxNu': boxNu, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        model = csParam.mappedValue('model', model)
        abode = csParam.mappedValue('abode', abode)
        purpose = csParam.mappedValue('purpose', purpose)
        boxNu = csParam.mappedValue('boxNu', boxNu)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        cmndClass = perfSiteRegContainer.ro_container_add
        cmndKwArgs = self.cmndCallTimeKwArgs()

        rpycInvResult =  cs.ro.roInvokeCmndAtSap(
            roSiteRegistrarSapPath,
            rtInv,
            cmndOutcome,
            cmndClass,
            ** cmndKwArgs,
        )

        return cmndOutcome

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reg_container_read" :comment "" :extent "verify" :ro "cli" :parsMand "model abode purpose containerNu" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reg_container_read>>  =verify= parsMand=model abode purpose containerNu ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class reg_container_read(cs.Cmnd):
    cmndParamsMandatory = [ 'model', 'abode', 'purpose', 'containerNu', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             model: typing.Optional[str]=None,  # Cs Mandatory Param
             abode: typing.Optional[str]=None,  # Cs Mandatory Param
             purpose: typing.Optional[str]=None,  # Cs Mandatory Param
             containerNu: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, 'containerNu': containerNu, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        model = csParam.mappedValue('model', model)
        abode = csParam.mappedValue('abode', abode)
        purpose = csParam.mappedValue('purpose', purpose)
        containerNu = csParam.mappedValue('containerNu', containerNu)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        cmndClass = perfSiteRegContainer.container_unitRead
        cmndKwArgs = self.cmndCallTimeKwArgs()

        rpycInvResult =  cs.ro.roInvokeCmndAtSap(
            roSiteRegistrarSapPath,
            rtInv,
            cmndOutcome,
            cmndClass,
            ** cmndKwArgs,
        )

        return cmndOutcome


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reg_container_update" :comment "" :extent "verify" :ro "cli" :parsMand "model abode purpose containerNu boxNu" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reg_container_update>>  =verify= parsMand=model abode purpose containerNu boxNu ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class reg_container_update(cs.Cmnd):
    cmndParamsMandatory = [ 'model', 'abode', 'purpose', 'containerNu', 'boxNu', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             model: typing.Optional[str]=None,  # Cs Mandatory Param
             abode: typing.Optional[str]=None,  # Cs Mandatory Param
             purpose: typing.Optional[str]=None,  # Cs Mandatory Param
             containerNu: typing.Optional[str]=None,  # Cs Mandatory Param
             boxNu: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, 'containerNu': containerNu, 'boxNu': boxNu, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        model = csParam.mappedValue('model', model)
        abode = csParam.mappedValue('abode', abode)
        purpose = csParam.mappedValue('purpose', purpose)
        containerNu = csParam.mappedValue('containerNu', containerNu)
        boxNu = csParam.mappedValue('boxNu', boxNu)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        cmndClass = perfSiteRegContainer.container_unitUpdate
        cmndKwArgs = self.cmndCallTimeKwArgs()

        rpycInvResult =  cs.ro.roInvokeCmndAtSap(
            roSiteRegistrarSapPath,
            rtInv,
            cmndOutcome,
            cmndClass,
            ** cmndKwArgs,
        )

        return cmndOutcome

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reg_container_delete" :comment "" :extent "verify" :ro "cli" :parsMand "model abode purpose containerNu" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reg_boxDelete>>  =verify= parsMand=model abode purpose containerNu ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class reg_boxDelete(cs.Cmnd):
    cmndParamsMandatory = [ 'model', 'abode', 'purpose', 'containerNu', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             model: typing.Optional[str]=None,  # Cs Mandatory Param
             abode: typing.Optional[str]=None,  # Cs Mandatory Param
             purpose: typing.Optional[str]=None,  # Cs Mandatory Param
             containerNu: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, 'containerNu': containerNu, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        model = csParam.mappedValue('model', model)
        abode = csParam.mappedValue('abode', abode)
        purpose = csParam.mappedValue('purpose', purpose)
        containerNu = csParam.mappedValue('containerNu', containerNu)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        cmndClass = perfSiteRegContainer.container_unitDelete
        cmndKwArgs = self.cmndCallTimeKwArgs()

        rpycInvResult =  cs.ro.roInvokeCmndAtSap(
            roSiteRegistrarSapPath,
            rtInv,
            cmndOutcome,
            cmndClass,
            ** cmndKwArgs,
        )

        return cmndOutcome


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reg_container_find" :comment "" :extent "verify" :ro "cli" :parsMand "model abode purpose" :parsOpt ""  :argsMin 2 :argsMax 2 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reg_container_find>>  =verify= parsMand=model abode purpose argsMin=2 argsMax=2 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class reg_container_find(cs.Cmnd):
    cmndParamsMandatory = [ 'model', 'abode', 'purpose', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 2, 'Max': 2,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             model: typing.Optional[str]=None,  # Cs Mandatory Param
             abode: typing.Optional[str]=None,  # Cs Mandatory Param
             purpose: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        model = csParam.mappedValue('model', model)
        abode = csParam.mappedValue('abode', abode)
        purpose = csParam.mappedValue('purpose', purpose)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        cmndClass = perfSiteRegContainer.container_unitsFind
        cmndKwArgs = self.cmndCallTimeKwArgs()

        rpycInvResult =  cs.ro.roInvokeCmndAtSap(
            roSiteRegistrarSapPath,
            rtInv,
            cmndOutcome,
            cmndClass,
            ** cmndKwArgs,
        )

        return cmndOutcome

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reg_container_list" :comment "" :extent "verify" :ro "cli" parsMand "model abode purpose" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reg_container_list>>  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class reg_container_list(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        cmndClass = perfSiteRegContainer.container_unitsList
        cmndKwArgs = self.cmndCallTimeKwArgs()

        rpycInvResult =  cs.ro.roInvokeCmndAtSap(
            roSiteRegistrarSapPath,
            rtInv,
            cmndOutcome,
            cmndClass,
            ** cmndKwArgs,
        )

        return cmndOutcome


####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
