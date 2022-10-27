/****************************************************************************
** Meta object code from reading C++ file 'MagCalDlg.h'
**
** Created by: The Qt Meta Object Compiler version 63 (Qt 4.8.7)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "../../RTIMULibDemo/MagCalDlg.h"
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'MagCalDlg.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 63
#error "This file was generated using the moc from 4.8.7. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
static const uint qt_meta_data_MagCalDlg[] = {

 // content:
       6,       // revision
       0,       // classname
       0,    0, // classinfo
       5,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: signature, parameters, type, tag, flags
      11,   10,   10,   10, 0x0a,
      22,   10,   10,   10, 0x0a,
      32,   10,   10,   10, 0x0a,
      47,   10,   10,   10, 0x0a,
      64,   59,   10,   10, 0x0a,

       0        // eod
};

static const char qt_meta_stringdata_MagCalDlg[] = {
    "MagCalDlg\0\0onCancel()\0onReset()\0"
    "onSaveMinMax()\0onProcess()\0data\0"
    "newIMUData(RTIMU_DATA)\0"
};

void MagCalDlg::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        Q_ASSERT(staticMetaObject.cast(_o));
        MagCalDlg *_t = static_cast<MagCalDlg *>(_o);
        switch (_id) {
        case 0: _t->onCancel(); break;
        case 1: _t->onReset(); break;
        case 2: _t->onSaveMinMax(); break;
        case 3: _t->onProcess(); break;
        case 4: _t->newIMUData((*reinterpret_cast< const RTIMU_DATA(*)>(_a[1]))); break;
        default: ;
        }
    }
}

const QMetaObjectExtraData MagCalDlg::staticMetaObjectExtraData = {
    0,  qt_static_metacall 
};

const QMetaObject MagCalDlg::staticMetaObject = {
    { &QDialog::staticMetaObject, qt_meta_stringdata_MagCalDlg,
      qt_meta_data_MagCalDlg, &staticMetaObjectExtraData }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &MagCalDlg::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *MagCalDlg::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *MagCalDlg::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_MagCalDlg))
        return static_cast<void*>(const_cast< MagCalDlg*>(this));
    return QDialog::qt_metacast(_clname);
}

int MagCalDlg::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QDialog::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 5)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 5;
    }
    return _id;
}
QT_END_MOC_NAMESPACE
