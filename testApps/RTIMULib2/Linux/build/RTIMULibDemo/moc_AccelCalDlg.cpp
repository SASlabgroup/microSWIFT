/****************************************************************************
** Meta object code from reading C++ file 'AccelCalDlg.h'
**
** Created by: The Qt Meta Object Compiler version 63 (Qt 4.8.7)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "../../RTIMULibDemo/AccelCalDlg.h"
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'AccelCalDlg.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 63
#error "This file was generated using the moc from 4.8.7. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
static const uint qt_meta_data_AccelCalDlg[] = {

 // content:
       6,       // revision
       0,       // classname
       0,    0, // classinfo
       6,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: signature, parameters, type, tag, flags
      13,   12,   12,   12, 0x0a,
      20,   12,   12,   12, 0x0a,
      31,   12,   12,   12, 0x0a,
      41,   12,   12,   12, 0x0a,
      54,   12,   12,   12, 0x0a,
      74,   69,   12,   12, 0x0a,

       0        // eod
};

static const char qt_meta_stringdata_AccelCalDlg[] = {
    "AccelCalDlg\0\0onOk()\0onCancel()\0onReset()\0"
    "onCheckAll()\0onUncheckAll()\0data\0"
    "newIMUData(RTIMU_DATA)\0"
};

void AccelCalDlg::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        Q_ASSERT(staticMetaObject.cast(_o));
        AccelCalDlg *_t = static_cast<AccelCalDlg *>(_o);
        switch (_id) {
        case 0: _t->onOk(); break;
        case 1: _t->onCancel(); break;
        case 2: _t->onReset(); break;
        case 3: _t->onCheckAll(); break;
        case 4: _t->onUncheckAll(); break;
        case 5: _t->newIMUData((*reinterpret_cast< const RTIMU_DATA(*)>(_a[1]))); break;
        default: ;
        }
    }
}

const QMetaObjectExtraData AccelCalDlg::staticMetaObjectExtraData = {
    0,  qt_static_metacall 
};

const QMetaObject AccelCalDlg::staticMetaObject = {
    { &QDialog::staticMetaObject, qt_meta_stringdata_AccelCalDlg,
      qt_meta_data_AccelCalDlg, &staticMetaObjectExtraData }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &AccelCalDlg::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *AccelCalDlg::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *AccelCalDlg::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_AccelCalDlg))
        return static_cast<void*>(const_cast< AccelCalDlg*>(this));
    return QDialog::qt_metacast(_clname);
}

int AccelCalDlg::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QDialog::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 6)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 6;
    }
    return _id;
}
QT_END_MOC_NAMESPACE
