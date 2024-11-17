"""
Extendeding and supplementing the widgets import bluesky-widgets
"""

import os

from bluesky_widgets.qt.run_engine_client import (
    QtReConsoleMonitor,
    QtReEnvironmentControls,
    QtReExecutionControls,
    QtReManagerConnection,
    QtRePlanEditor,
    QtRePlanHistory,
    QtRePlanQueue,
    QtReQueueControls,
    QtReRunningPlan,
    QtReStatusMonitor,
)
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class QtOrganizeQueueWidgets(QSplitter):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model

        self.setOrientation(Qt.Vertical)

        self._frame_1 = QFrame(self)
        self._frame_2 = QFrame(self)
        self._frame_3 = QFrame(self)
        self._frame_4 = QFrame(self)

        self.addWidget(self._frame_1)
        self.addWidget(self._frame_2)
        self.addWidget(self._frame_3)
        self.addWidget(self._frame_4)

        self._running_plan = QtReRunningPlan(model)
        self._running_plan.monitor_mode = True
        self._plan_queue = QtRePlanQueue(model)
        self._plan_queue.monitor_mode = True
        self._plan_history = QtRePlanHistory(model)
        self._plan_history.monitor_mode = True
        self._console_monitor = QtReConsoleMonitor(model)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self._running_plan)
        self._frame_1.setLayout(vbox)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self._plan_queue)
        self._frame_2.setLayout(vbox)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self._plan_history)
        self._frame_3.setLayout(vbox)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self._console_monitor)
        self._frame_4.setLayout(vbox)

        h = self.sizeHint().height()
        self.setSizes([h, 2 * h, 2 * h, h])


class QtRunEngineManager_Monitor(QWidget):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(QtReManagerConnection(model))
        hbox.addWidget(QtReStatusMonitor(model))
        hbox.addStretch()
        vbox.addLayout(hbox)

        vbox.addWidget(QtOrganizeQueueWidgets(model), stretch=2)

        self.setLayout(vbox)


class QtRunEngineManager_Editor(QWidget):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(QtReEnvironmentControls(model))
        hbox.addWidget(QtReQueueControls(model))
        hbox.addWidget(QtReExecutionControls(model))
        hbox.addWidget(QtReStatusMonitor(model))

        hbox.addStretch()
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        vbox1 = QVBoxLayout()

        # Register plan editor (opening plans in the editor by double-clicking the plan in the table)
        pe = QtRePlanEditor(model)
        pq = QtRePlanQueue(model)
        pq.registered_item_editors.append(pe.edit_queue_item)

        vbox1.addWidget(pe, stretch=1)
        vbox1.addWidget(pq, stretch=1)
        hbox.addLayout(vbox1)
        vbox2 = QVBoxLayout()
        vbox2.addWidget(QtReRunningPlan(model), stretch=1)
        vbox2.addWidget(QtRePlanHistory(model), stretch=2)
        hbox.addLayout(vbox2)
        vbox.addLayout(hbox)
        self.setLayout(vbox)


class QtScriptAdder(QWidget):
    def __init__(self, model, base_script_dir, parent=None):
        super().__init__(parent)
        self.model = model
        self.base_script_dir = base_script_dir

        self.base_dir_label = QLabel("Base Directory Path:")
        self.base_dir_edit = QLineEdit()
        self.base_dir_edit.setText(self.base_script_dir)
        self.base_dir_edit.setReadOnly(True)
        self.base_dir_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.script_label = QLabel("Script:")
        self.script_edit = QLineEdit()
        self.script_edit.setReadOnly(True)
        self.script_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.add_script_button = QPushButton("Add Script")
        self.add_script_button.clicked.connect(self.select_script)
        self.add_script_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.add_plan_button = QPushButton("Add Plan")
        self.add_plan_button.clicked.connect(self.add_plan)
        self.add_plan_button.setEnabled(False)
        self.add_plan_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.addRow(self.base_dir_label, self.base_dir_edit)
        form_layout.addRow(self.script_label, self.script_edit)
        layout.addLayout(form_layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.add_script_button)
        buttons_layout.addWidget(self.add_plan_button)
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        layout.addStretch()

        self.setLayout(layout)

        self.selected_script_path = None

    def select_script(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Script File", self.base_script_dir, "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            if not os.path.commonpath([file_path, self.base_script_dir]) == self.base_script_dir:
                QMessageBox.warning(self, "Invalid Selection", "Please select a script within the base directory.")
                return
            self.selected_script_path = file_path
            relative_path = os.path.relpath(file_path, self.base_script_dir)
            self.script_edit.setText(relative_path)
            self.add_plan_button.setEnabled(True)
        else:
            self.add_plan_button.setEnabled(False)
            self.script_edit.clear()
            self.selected_script_path = None

    def add_plan(self):
        if self.selected_script_path:
            try:
                plan = {
                    "name": "run_with_logging",
                    "args": [self.selected_script_path],
                    "kwargs": {},
                    "item_type": "plan",
                }
                self.model.queue_item_add(item=plan)
                QMessageBox.information(self, "Success", "Added script to the queue.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add plan: {e}")
        else:
            QMessageBox.warning(self, "No Script Selected", "Please select a script before adding a plan.")


class ExtendedQtRePlanEditor(QtRePlanEditor):
    def __init__(self, model, base_script_dir, *args, **kwargs):
        super().__init__(model, *args, **kwargs)

        self.base_script_dir = base_script_dir

        self.script_adder = QtScriptAdder(model, base_script_dir)
        self._tab_widget.addTab(self.script_adder, "Script Runner")


class QtRunEngineManager_Scripts(QWidget):
    def __init__(self, model, base_script_dir, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        self.base_script_dir = base_script_dir

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()

        hbox.addWidget(QtReEnvironmentControls(model))
        hbox.addWidget(QtReQueueControls(model))
        hbox.addWidget(QtReExecutionControls(model))
        hbox.addWidget(QtReStatusMonitor(model))

        hbox.addStretch()
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        vbox1 = QVBoxLayout()

        pe = ExtendedQtRePlanEditor(model, base_script_dir)
        pq = QtRePlanQueue(model)
        pq.registered_item_editors.append(pe.edit_queue_item)

        vbox1.addWidget(pe, stretch=1)
        vbox1.addWidget(pq, stretch=1)
        hbox.addLayout(vbox1)

        vbox2 = QVBoxLayout()
        vbox2.addWidget(QtReRunningPlan(model), stretch=1)
        vbox2.addWidget(QtRePlanHistory(model), stretch=2)
        hbox.addLayout(vbox2)

        vbox.addLayout(hbox)
        self.setLayout(vbox)


class QtViewer(QTabWidget):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model

        base_script_dir = os.environ.get("SCRIPT_DIRECTORY_PATH", "~/.ipython/profile_default/startup/scripts")
        base_script_dir = os.path.abspath(os.path.expanduser(base_script_dir))

        self.setTabPosition(QTabWidget.West)

        self._re_manager_monitor = QtRunEngineManager_Monitor(model.run_engine)
        self.addTab(self._re_manager_monitor, "Monitor Queue")

        self._re_manager_editor = QtRunEngineManager_Editor(model.run_engine)
        self.addTab(self._re_manager_editor, "Edit and Control Queue")

        self._re_manager_scripts = QtRunEngineManager_Scripts(model.run_engine, base_script_dir)
        self.addTab(self._re_manager_scripts, "Scripts")
