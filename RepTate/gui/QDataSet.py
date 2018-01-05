# RepTate: Rheology of Entangled Polymers: Toolkit for the Analysis of Theory and Experiments
# http://blogs.upm.es/compsoftmatter/software/reptate/
# https://github.com/jorge-ramirez-upm/RepTate
# http://reptate.readthedocs.io
# Jorge Ramirez, jorge.ramirez@upm.es
# Victor Boudara, mmvahb@leeds.ac.uk
# Copyright (2017) Universidad Politécnica de Madrid, University of Leeds
# This software is distributed under the GNU General Public License. 
"""Module QDataSet

Module that defines the GUI counterpart of Dataset.

""" 
from os.path import dirname, join, abspath
from PyQt5.QtGui import QPixmap, QColor, QPainter, QIcon
from PyQt5.uic import loadUiType
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QWidget, QTreeWidget, QTreeWidgetItem, QTabWidget, QHeaderView, QToolBar, QComboBox, QMessageBox, QInputDialog, QFrame, QToolButton, QMenu, QAction, QAbstractItemView, QTableWidgetItem
from DataSet import DataSet
from QTheory import QTheory
from DataSetWidget import DataSetWidget
import threading

PATH = dirname(abspath(__file__))
Ui_DataSet, QWidget = loadUiType(join(PATH,'DataSet.ui'))


class QDataSet(DataSet, QWidget, Ui_DataSet):
    """[summary]
    
    [description]
    """
    def __init__(self, name="QDataSet", parent=None):
        """Constructor
        
        [description]
        
        Keyword Arguments:
            name {[type]} -- [description] (default: {"QDataSet"})
            parent {[type]} -- [description] (default: {None})
        """
        super().__init__(name=name, parent=parent)
        QWidget.__init__(self)
        Ui_DataSet.__init__(self)

        self.setupUi(self)
        self.selected_file = None


        self.DataSettreeWidget = DataSetWidget(self)
        self.splitter.insertWidget(0, self.DataSettreeWidget)

        self.DataSettreeWidget.setIndentation(0)
        self.DataSettreeWidget.setHeaderItem(QTreeWidgetItem([""]))   
        self.DataSettreeWidget.setSelectionMode(1) #QAbstractItemView::SingleSelection
        hd = self.DataSettreeWidget.header()
        hd.setSectionsMovable(False)
        w = self.DataSettreeWidget.width()
        w /= hd.count()
        for i in range(hd.count()):
            hd.resizeSection(0, w)

        # Theory Toolbar
        tb = QToolBar()
        tb.setIconSize(QSize(24,24))
        tb.addAction(self.actionNew_Theory)
        self.cbtheory = QComboBox()
        self.cbtheory.setToolTip("Choose a Theory")
        # self.cbtheory.addItem("Select Theory")
        # self.cbtheory.model().item(0).setEnabled(False)

        for th_name in sorted(self.parent_application.theories):
             self.cbtheory.addItem(th_name)
        self.cbtheory.setCurrentIndex(0)
        
        ###

        self.cbtheory.setMaximumWidth(115)
        self.cbtheory.setMinimumWidth(50)
        tb.addWidget(self.cbtheory)
        tb.addAction(self.actionCalculate_Theory)
        tb.addAction(self.actionMinimize_Error)
        #Buttons not wired yet
        # tb.addAction(self.actionTheory_Options)
        # self.actionTheory_Options.setDisabled(True)
        tbut = QToolButton()
        tbut.setPopupMode(QToolButton.MenuButtonPopup)
        tbut.setDefaultAction(self.actionShow_Limits)
        menu = QMenu()
        menu.addAction(self.actionVertical_Limits)
        menu.addAction(self.actionHorizontal_Limits)
        tbut.setMenu(menu)
        tb.addWidget(tbut)
        self.TheoryLayout.insertWidget(0, tb)
        self.splitter.setSizes((3, 2))

        #desactive buttons when no theory tab
        self.theory_actions_disabled(True)

        connection_id = self.actionNew_Theory.triggered.connect(self.handle_actionNew_Theory)
        connection_id = self.DataSettreeWidget.itemChanged.connect(self.handle_itemChanged)
        # connection_id = self.DataSettreeWidget.itemClicked.connect(self.handle_itemClicked)
        connection_id = self.DataSettreeWidget.itemDoubleClicked.connect(self.handle_itemDoubleClicked)
        connection_id = self.DataSettreeWidget.header().sortIndicatorChanged.connect(self.handle_sortIndicatorChanged)
        connection_id = self.DataSettreeWidget.itemSelectionChanged.connect(self.handle_itemSelectionChanged)
        # connection_id = self.DataSettreeWidget.currentItemChanged.connect(self.handle_currentItemChanged)

        connection_id = self.TheorytabWidget.tabCloseRequested.connect(self.handle_thTabCloseRequested)
        connection_id = self.TheorytabWidget.tabBarDoubleClicked.connect(self.handle_thTabBarDoubleClicked)
        connection_id = self.TheorytabWidget.currentChanged.connect(self.handle_thCurrentChanged)
        connection_id = self.actionMinimize_Error.triggered.connect(self.handle_actionMinimize_Error)
        connection_id = self.actionCalculate_Theory.triggered.connect(self.handle_actionCalculate_Theory)

        connection_id = self.actionVertical_Limits.triggered.connect(self.toggle_vertical_limits)
        connection_id = self.actionHorizontal_Limits.triggered.connect(self.toggle_horizontal_limits)        
    
    def set_table_icons(self, table_icon_list):
        """The list 'table_icon_list' contains tuples (file_name_short, marker_name, face, color)
        
        [description]
        
        Arguments:
            table_icon_list {[type]} -- [description]
        """
        self.DataSettreeWidget.blockSignals(True) #avoid triggering 'itemChanged' signal that causes a call to do_plot()
        
        for fname, marker_name, face, color in table_icon_list:
            item = self.DataSettreeWidget.findItems(fname, Qt.MatchCaseSensitive, column=0) #returns list of items matching file name
            if item:
                #paint icon
                folder = ':/Markers/Images/Matplotlib_markers/'
                if face == 'none': #empty symbol
                    marker_path = folder + 'marker_%s'%marker_name
                else: #filled symbol
                    marker_path = folder + 'marker_filled_%s'%marker_name
                qp = QPixmap(marker_path)
                mask = qp.createMaskFromColor(QColor(0, 0, 0), Qt.MaskOutColor)
                qpainter = QPainter()
                qpainter.begin(qp)
                qpainter.setPen(QColor(int(255*color[0]),int(255*color[1]),int(255*color[2]),255))
                qpainter.drawPixmap(qp.rect(),mask,qp.rect())
                qpainter.end()
                item[0].setIcon(0, QIcon(qp))
            
        self.DataSettreeWidget.blockSignals(False)

    def theory_actions_disabled(self, state):
        """Disable theory buttons if no theory tab is open
        
        [description]
        
        Arguments:
            state {[type]} -- [description]
        """
        self.actionCalculate_Theory.setDisabled(state)
        self.actionMinimize_Error.setDisabled(state)
        # self.actionTheory_Options.setDisabled(state)
        self.actionShow_Limits.setDisabled(state)
        self.actionVertical_Limits.setDisabled(state)
        self.actionHorizontal_Limits.setDisabled(state)

    def set_limit_icon(self):
        """[summary]
        
        [description]
        """
        hlim = self.actionHorizontal_Limits.isChecked()
        vlim = self.actionVertical_Limits.isChecked()
        if hlim and vlim:
            img = "Line Chart Both Limits"
        elif vlim:
            img = "Line Chart Vertical Limits"
        elif hlim:
            img = "Line Chart Horizontal Limits"
        else:
            img = "Line Chart"
        self.actionShow_Limits.setIcon(QIcon(':/Images/Images/%s'%img))

    def set_no_limits(self, th_name):
        """Turn the x and yrange selectors off
        
        [description]
        
        Arguments:
            th_name {[type]} -- [description]
        """
        if th_name in self.theories:
            th = self.theories[self.current_theory]
            th.xrange.set_visible(False) 
            th.xminline.set_visible(False) 
            th.xmaxline.set_visible(False) 

            th.yrange.set_visible(False) 
            th.yminline.set_visible(False) 
            th.ymaxline.set_visible(False) 

            self.actionHorizontal_Limits.setChecked(False)
            self.actionVertical_Limits.setChecked(False)
            self.set_limit_icon()

    def toggle_vertical_limits(self):
        """Show/Hide the xrange selector for fit
        
        [description]
        """
        if self.current_theory:
            self.theories[self.current_theory].do_xrange("")
            self.set_limit_icon()
 
    def toggle_horizontal_limits(self):
        """Show/Hide the yrange selector for fit
        
        [description]
        """
        if self.current_theory:        
            self.theories[self.current_theory].do_yrange("")
            self.set_limit_icon()


    def handle_actionCalculate_Theory(self):
        if self.current_theory and self.files:
            th = self.theories[self.current_theory]
            if th.calculate_is_busy or th.is_fitting or th.thread_calc_busy or th.thread_fit_busy: #do nothing if already busy in do_calculate or do_fit
                return
            th.handle_actionCalculate_Theory()
    #         if th.calculate_is_busy or th.is_fitting or self.thread_calc_busy or self.thread_fit_busy: #do nothing if already busy in do_calculate or do_fit
    #             return
    #         self.thread_calc_busy = True
    #         self.actionCalculate_Theory.setDisabled(True)
    #         print("handle_actionCalculate_Theory thread started")
    #         self.thread_calc = CalculateThread(self.end_thread_calc, th.do_calculate, "", )
    #         self.thread_calc.start()
    #         print("handle_actionCalculate_Theory thread ended")
    
    # def end_thread_calc(self):
    #     self.theories[self.current_theory].update_parameter_table()
    #     self.parent_application.update_Qplot()
    #     self.thread_calc_busy = False
    #     self.actionCalculate_Theory.setDisabled(False)





    # def handle_actionCalculate_Theory_(self, th):
    #     """Calculate the theory
        
    #     [description]
    #     """
    #     print("begin do_calculate")
    #     th.do_calculate("")
    #     print("end do_calculate")
        # th.update_parameter_table()
        # self.parent_application.update_Qplot()

    # def handle_actionMinimize_Error(self):
    #     if self.current_theory and self.files:
    #         th = self.theories[self.current_theory]
    #         if th.calculate_is_busy or th.is_fitting: #do nothing if already busy in do_calculate or do_fit
    #             return
    #         if th.single_file and len(self.files)-len(self.inactive_files)>1: 
    #             header = "New Theory"
    #             message = "Theory \"%s\" cannot be applied to multiple data files"%self.current_theory
    #             QMessageBox.warning(self, header, message)
    #             return

    #         thread1 = CalculateThread(self.handle_actionMinimize_Error_, th)
    #         thread1.start()


    def handle_actionMinimize_Error(self):
        """Minimize the error
        
        [description]
        """
        if self.current_theory and self.files:
            th = self.theories[self.current_theory]
            if th.calculate_is_busy or th.is_fitting or th.thread_calc_busy or th.thread_fit_busy: #do nothing if already busy in do_calculate or do_fit
                return
            if th.single_file and (len(self.files) - len(self.inactive_files))>1: 
                header = "New Theory"
                message = "Theory \"%s\" cannot be applied to multiple data files"%self.current_theory
                QMessageBox.warning(self, header, message)
                return
            th.handle_actionMinimize_Error()
    #         if th.calculate_is_busy or th.is_fitting or self.thread_fit_busy or self.thread_calc_busy: #do nothing if already busy in do_calculate or do_fit
    #             return
    #         if th.single_file and len(self.files)-len(self.inactive_files)>1: 
    #             header = "New Theory"
    #             message = "Theory \"%s\" cannot be applied to multiple data files"%self.current_theory
    #             QMessageBox.warning(self, header, message)
    #             return
            
    #         self.thread_fit_busy = True
    #         self.actionMinimize_Error.setDisabled(True)
    #         self.thread_fit = CalculateThread(self.end_thread_fit, th.do_fit, "", )
    #         self.thread_fit.start()

    # def end_thread_fit(self):
    #     self.theories[self.current_theory].update_parameter_table()
    #     self.parent_application.update_Qplot()
    #     self.thread_fit_busy = False
    #     self.actionMinimize_Error.setDisabled(False)


    def handle_thCurrentChanged(self, index):
        """Change figure when the active theory tab is changed
        
        [description]
        
        Arguments:
            index {[type]} -- [description]
        """
        th = self.TheorytabWidget.widget(index)
        if th:
            self.current_theory = th.name
            th.do_show()
            ntab = self.TheorytabWidget.count()
            #hide all theory curves
            for i in range(ntab):   
                if i != index:
                    th_to_hide = self.TheorytabWidget.widget(i)
                    th_to_hide.do_hide()
        else:
            self.current_theory = None
            self.theory_actions_disabled(True)
        if th.thread_calc_busy or th.thread_fit_busy:
            return
        self.parent_application.update_plot()
        self.parent_application.update_Qplot()

    def Qshow_all(self):
        """Show all the files in this dataset, except those previously hiden
        
        [description]
        """
        self.do_show_all()
        for i in range(self.DataSettreeWidget.topLevelItemCount()):
            file_name = self.DataSettreeWidget.topLevelItem(i).text(0)
            if file_name in self.inactive_files:
                self.DataSettreeWidget.topLevelItem(i).setCheckState(0, 0)
            else:
                self.DataSettreeWidget.topLevelItem(i).setCheckState(0, 2)


    def handle_thTabBarDoubleClicked(self, index):
        """Edit Theory name
        
        [description]
        
        Arguments:
            index {[type]} -- [description]
        """
        old_name = self.TheorytabWidget.tabText(index)
        dlg = QInputDialog(self)
        dlg.setWindowTitle("Change Theory Name")
        dlg.setLabelText("New Theory Name:")
        dlg.setTextValue(old_name)
        dlg.resize(400,100)
        success = dlg.exec()
        new_tab_name = dlg.textValue()
        if (success and new_tab_name!=""):    
            self.TheorytabWidget.setTabText(index, new_tab_name)
            self.theories[old_name].name = new_tab_name
            self.theories[new_tab_name] = self.theories.pop(old_name)
            self.current_theory = new_tab_name

    def handle_thTabCloseRequested(self, index):
        """Delete a theory tab from the current dataset
        
        [description]
        
        Arguments:
            index {[type]} -- [description]
        """
        th_name = self.TheorytabWidget.widget(index).name
        self.set_no_limits(th_name)
        self.do_theory_delete(th_name) #call DataSet.do_theory_delete 
        self.TheorytabWidget.removeTab(index)


    def handle_itemSelectionChanged(self):
        """Define actions for when a file table is selected
        
        [description]
        """
        selection = self.DataSettreeWidget.selectedItems()
        if selection==[]:
            self.selected_file = None
            self.highlight_series()
            return
        for f in self.files:
            if f.file_name_short==selection[0].text(0):  
                self.parent_application.disconnect_curve_drag()  
                self.selected_file = f
                self.highlight_series()
                self.populate_inspector()

    def highlight_series(self):
        """Highligh the data series of the selected file
        
        [description]
        """
        self.do_plot() #remove current series highlight
        file = self.selected_file
        if file is not None:
            view = self.parent_application.current_view
            for i in range(file.data_table.MAX_NUM_SERIES):
                    if (i<view.n and file.active):
                        file.data_table.series[i].set_marker('.')
                        # file.data_table.series[i].set_linestyle(":")
                        file.data_table.series[i].set_markerfacecolor("black")
                        file.data_table.series[i].set_markeredgecolor("black")
                        file.data_table.series[i].set_zorder(self.parent_application.zorder) #put series on top
            self.parent_application.zorder += 1
        self.parent_application.update_plot()

    def populate_inspector(self):
        """[summary]
        
        [description]
        """
        file = self.selected_file
        if not file: 
            self.parent_application.inspector_table.setRowCount(0)
            self.parent_application.DataInspectordockWidget.setWindowTitle("File:")
            return
        if self.parent_application.DataInspectordockWidget.isHidden():
            return
        dt = file.data_table
        nrow = dt.num_rows
        ncol = dt.num_columns
        inspec_tab = self.parent_application.inspector_table
        inspec_tab.setRowCount(nrow)
        inspec_tab.setColumnCount(ncol)
        for i in range(nrow):
            for j in range(ncol):
                x = "%.3e" %dt.data[i, j]
                inspec_tab.setItem(i, j, QTableWidgetItem(x)) # dt.setItem(row, column, item)
        ds_index = self.parent_application.DataSettabWidget.currentIndex()
        self.parent_application.DataInspectordockWidget.setWindowTitle(
            "File: \"%s\" in %s"%(file.file_name_short, self.parent_application.DataSettabWidget.tabText(ds_index)))
        
    def handle_itemChanged(self, item, column):
        """[summary]
        
        [description]
        
        Arguments:
            item {[type]} -- [description]
            column {[type]} -- [description]
        """
        if column == 0:
            self.change_file_visibility(item.text(0), item.checkState(column)==Qt.Checked)
 
    def handle_sortIndicatorChanged(self, column, order):
        """Sort files according to the selected parameter (column) and replot
        
        [description]
        
        Arguments:
            column {[type]} -- [description]
            order {[type]} -- [description]
        """
        # if column == 0: #do not sort file name
        #     return
        sort_param = self.DataSettreeWidget.headerItem().text(column)
        rev = True if order==Qt.AscendingOrder else False
        if rev:
            sort_param = sort_param + ",reverse"
        self.do_sort(sort_param)
        self.do_plot()
        self.set_table_icons(self.table_icon_list)

    def Qshow_all(self):
        """Show all the files in this dataset, except those previously hiden
        
        [description]
        """
        self.do_show_all()
        for i in range(self.DataSettreeWidget.topLevelItemCount()):
            file_name = self.DataSettreeWidget.topLevelItem(i).text(0)
            if file_name in self.inactive_files:
                self.DataSettreeWidget.topLevelItem(i).setCheckState(0, 0)
            else:
                self.DataSettreeWidget.topLevelItem(i).setCheckState(0, 2)

    def resizeEvent(self, evt=None):
        """[summary]
        
        [description]
        
        Keyword Arguments:
            evt {[type]} -- [description] (default: {None})
        """
        hd=self.DataSettreeWidget.header()
        w=self.DataSettreeWidget.width()
        w/=hd.count()
        for i in range(hd.count()):
            hd.resizeSection(i, w)        
            #hd.setTextAlignment(i, Qt.AlignHCenter)

    def handle_itemDoubleClicked(self, item, column):
        """Edit item entry upon double click
        
        [description]
        
        Arguments:
            item {[type]} -- [description]
            column {[type]} -- [description]
        """
        if column>0:
            param = self.DataSettreeWidget.headerItem().text(column) #retrive parameter name
            file_name_short = item.text(0) #retrive file name
            header = "Edit Parameter"
            message = "Do you want to edit %s of \"%s\"?"%(param, file_name_short)
            answer = QMessageBox.question(self, header, message)
            if answer == QMessageBox.Yes:
                old_value = item.text(column) #old parameter value       
                message = "New value of %s"%param
                new_value, success = QInputDialog.getDouble(self, header, message, float(old_value))
                if success:
                    for file in self.files:
                        if file.file_name_short == file_name_short:
                            file.file_parameters[param] = new_value #change value in DataSet
                    self.DataSettreeWidget.blockSignals(True) #avoid triggering 'itemChanged' signal that causes a false checkbox change
                    item.setText(column, str(new_value)) #change table label
                    self.DataSettreeWidget.blockSignals(False)

    def handle_actionNew_Theory(self):
        """Create new theory and do fit
        
        [description]
        """
        #if self.cbtheory.currentIndex() == 0:
        #    return
        th_name = self.cbtheory.currentText()
        #self.cbtheory.setCurrentIndex(0) # reset the combobox selection
        if th_name!='':
            self.new_theory(th_name)

    def new_theory(self, th_name, th_tab_id=""):
        """[summary]
        
        [description]
        
        Arguments:
            th_name {[type]} -- [description]
        """
        if not self.files:
            return
        if self.current_theory:
            self.set_no_limits(self.current_theory) #remove the xy-range limits
        self.theory_actions_disabled(False) #enable theory buttons
        newth = self.do_theory_new(th_name)

        # add new theory tab
        if th_tab_id == "": 
            th_tab_id = newth.name
            th_tab_id = ''.join(c for c in th_tab_id if c.isupper()) #get the upper case letters of th_name
            th_tab_id = "%s%d"%(th_tab_id, self.num_theories) #append number
        index = self.TheorytabWidget.addTab(newth, th_tab_id) #add theory tab
        self.TheorytabWidget.setCurrentIndex(index) #set new theory tab as curent tab
        #self.handle_thCurrentChanged(index)
        newth.update_parameter_table()
