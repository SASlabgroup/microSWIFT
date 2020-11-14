/********************************************************************************
** Form generated from reading UI file 'RTIMULibDemo.ui'
**
** Created by: Qt User Interface Compiler version 4.8.7
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_RTIMULIBDEMO_H
#define UI_RTIMULIBDEMO_H

#include <QtCore/QVariant>
#include <QtGui/QAction>
#include <QtGui/QApplication>
#include <QtGui/QButtonGroup>
#include <QtGui/QHeaderView>
#include <QtGui/QMainWindow>
#include <QtGui/QMenu>
#include <QtGui/QMenuBar>
#include <QtGui/QStatusBar>
#include <QtGui/QToolBar>
#include <QtGui/QWidget>

QT_BEGIN_NAMESPACE

class Ui_RTIMULibDemoClass
{
public:
    QAction *actionSelectIMU;
    QAction *actionSelectFusionAlgorithm;
    QAction *actionCalibrateMagnetometers;
    QAction *actionCalibrateAccelerometers;
    QAction *actionExit;
    QWidget *centralWidget;
    QMenuBar *menuBar;
    QMenu *menuActions;
    QStatusBar *statusBar;
    QToolBar *toolBar;

    void setupUi(QMainWindow *RTIMULibDemoClass)
    {
        if (RTIMULibDemoClass->objectName().isEmpty())
            RTIMULibDemoClass->setObjectName(QString::fromUtf8("RTIMULibDemoClass"));
        RTIMULibDemoClass->resize(658, 562);
        RTIMULibDemoClass->setMinimumSize(QSize(0, 0));
        actionSelectIMU = new QAction(RTIMULibDemoClass);
        actionSelectIMU->setObjectName(QString::fromUtf8("actionSelectIMU"));
        actionSelectFusionAlgorithm = new QAction(RTIMULibDemoClass);
        actionSelectFusionAlgorithm->setObjectName(QString::fromUtf8("actionSelectFusionAlgorithm"));
        actionCalibrateMagnetometers = new QAction(RTIMULibDemoClass);
        actionCalibrateMagnetometers->setObjectName(QString::fromUtf8("actionCalibrateMagnetometers"));
        actionCalibrateAccelerometers = new QAction(RTIMULibDemoClass);
        actionCalibrateAccelerometers->setObjectName(QString::fromUtf8("actionCalibrateAccelerometers"));
        actionExit = new QAction(RTIMULibDemoClass);
        actionExit->setObjectName(QString::fromUtf8("actionExit"));
        centralWidget = new QWidget(RTIMULibDemoClass);
        centralWidget->setObjectName(QString::fromUtf8("centralWidget"));
        centralWidget->setMinimumSize(QSize(400, 300));
        RTIMULibDemoClass->setCentralWidget(centralWidget);
        menuBar = new QMenuBar(RTIMULibDemoClass);
        menuBar->setObjectName(QString::fromUtf8("menuBar"));
        menuBar->setGeometry(QRect(0, 0, 658, 25));
        menuActions = new QMenu(menuBar);
        menuActions->setObjectName(QString::fromUtf8("menuActions"));
        RTIMULibDemoClass->setMenuBar(menuBar);
        statusBar = new QStatusBar(RTIMULibDemoClass);
        statusBar->setObjectName(QString::fromUtf8("statusBar"));
        RTIMULibDemoClass->setStatusBar(statusBar);
        toolBar = new QToolBar(RTIMULibDemoClass);
        toolBar->setObjectName(QString::fromUtf8("toolBar"));
        RTIMULibDemoClass->addToolBar(Qt::TopToolBarArea, toolBar);

        menuBar->addAction(menuActions->menuAction());
        menuActions->addAction(actionSelectFusionAlgorithm);
        menuActions->addAction(actionSelectIMU);
        menuActions->addAction(actionCalibrateAccelerometers);
        menuActions->addAction(actionCalibrateMagnetometers);
        menuActions->addAction(actionExit);
        toolBar->addAction(actionSelectIMU);
        toolBar->addSeparator();
        toolBar->addAction(actionSelectFusionAlgorithm);
        toolBar->addSeparator();
        toolBar->addAction(actionCalibrateAccelerometers);
        toolBar->addSeparator();
        toolBar->addAction(actionCalibrateMagnetometers);
        toolBar->addSeparator();
        toolBar->addAction(actionExit);
        toolBar->addSeparator();

        retranslateUi(RTIMULibDemoClass);

        QMetaObject::connectSlotsByName(RTIMULibDemoClass);
    } // setupUi

    void retranslateUi(QMainWindow *RTIMULibDemoClass)
    {
        RTIMULibDemoClass->setWindowTitle(QApplication::translate("RTIMULibDemoClass", "RTIMULibDemo", 0, QApplication::UnicodeUTF8));
        actionSelectIMU->setText(QApplication::translate("RTIMULibDemoClass", "Select IMU", 0, QApplication::UnicodeUTF8));
        actionSelectFusionAlgorithm->setText(QApplication::translate("RTIMULibDemoClass", "Select fusion algorithm", 0, QApplication::UnicodeUTF8));
        actionCalibrateMagnetometers->setText(QApplication::translate("RTIMULibDemoClass", "Calibrate magnetometers", 0, QApplication::UnicodeUTF8));
        actionCalibrateAccelerometers->setText(QApplication::translate("RTIMULibDemoClass", "Calibrate accelerometers", 0, QApplication::UnicodeUTF8));
        actionExit->setText(QApplication::translate("RTIMULibDemoClass", "Exit", 0, QApplication::UnicodeUTF8));
        menuActions->setTitle(QApplication::translate("RTIMULibDemoClass", "Actions", 0, QApplication::UnicodeUTF8));
        toolBar->setWindowTitle(QApplication::translate("RTIMULibDemoClass", "toolBar", 0, QApplication::UnicodeUTF8));
    } // retranslateUi

};

namespace Ui {
    class RTIMULibDemoClass: public Ui_RTIMULibDemoClass {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_RTIMULIBDEMO_H
