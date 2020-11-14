/****************************************************************************
** Meta object code from reading C++ file 'IMUThread.h'
**
** Created by: The Qt Meta Object Compiler version 63 (Qt 4.8.7)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "../../RTIMULibDemo/IMUThread.h"
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'IMUThread.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 63
#error "This file was generated using the moc from 4.8.7. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
static const uint qt_meta_data_IMUThread[] = {

 // content:
       6,       // revision
       0,       // classname
       0,    0, // classinfo
      10,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       5,       // signalCount

 // signals: signature, parameters, type, tag, flags
      11,   10,   10,   10, 0x05,
      21,   10,   10,   10, 0x05,
      41,   10,   10,   10, 0x05,
      70,   62,   10,   10, 0x05,
      97,   92,   10,   10, 0x05,

 // slots: signature, parameters, type, tag, flags
     120,   10,   10,   10, 0x0a,
     138,   10,   10,   10, 0x0a,
     148,   10,   10,   10, 0x0a,
     157,   10,   10,   10, 0x0a,
     171,   10,   10,   10, 0x0a,

       0        // eod
};

static const char qt_meta_stringdata_IMUThread[] = {
    "IMUThread\0\0running()\0internalEndThread()\0"
    "internalKillThread()\0compass\0"
    "newCalData(RTVector3)\0data\0"
    "newIMUData(RTIMU_DATA)\0internalRunLoop()\0"
    "cleanup()\0newIMU()\0newPressure()\0"
    "newHumidity()\0"
};

void IMUThread::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        Q_ASSERT(staticMetaObject.cast(_o));
        IMUThread *_t = static_cast<IMUThread *>(_o);
        switch (_id) {
        case 0: _t->running(); break;
        case 1: _t->internalEndThread(); break;
        case 2: _t->internalKillThread(); break;
        case 3: _t->newCalData((*reinterpret_cast< const RTVector3(*)>(_a[1]))); break;
        case 4: _t->newIMUData((*reinterpret_cast< const RTIMU_DATA(*)>(_a[1]))); break;
        case 5: _t->internalRunLoop(); break;
        case 6: _t->cleanup(); break;
        case 7: _t->newIMU(); break;
        case 8: _t->newPressure(); break;
        case 9: _t->newHumidity(); break;
        default: ;
        }
    }
}

const QMetaObjectExtraData IMUThread::staticMetaObjectExtraData = {
    0,  qt_static_metacall 
};

const QMetaObject IMUThread::staticMetaObject = {
    { &QObject::staticMetaObject, qt_meta_stringdata_IMUThread,
      qt_meta_data_IMUThread, &staticMetaObjectExtraData }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &IMUThread::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *IMUThread::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *IMUThread::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_IMUThread))
        return static_cast<void*>(const_cast< IMUThread*>(this));
    return QObject::qt_metacast(_clname);
}

int IMUThread::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QObject::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 10)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 10;
    }
    return _id;
}

// SIGNAL 0
void IMUThread::running()
{
    QMetaObject::activate(this, &staticMetaObject, 0, 0);
}

// SIGNAL 1
void IMUThread::internalEndThread()
{
    QMetaObject::activate(this, &staticMetaObject, 1, 0);
}

// SIGNAL 2
void IMUThread::internalKillThread()
{
    QMetaObject::activate(this, &staticMetaObject, 2, 0);
}

// SIGNAL 3
void IMUThread::newCalData(const RTVector3 & _t1)
{
    void *_a[] = { 0, const_cast<void*>(reinterpret_cast<const void*>(&_t1)) };
    QMetaObject::activate(this, &staticMetaObject, 3, _a);
}

// SIGNAL 4
void IMUThread::newIMUData(const RTIMU_DATA & _t1)
{
    void *_a[] = { 0, const_cast<void*>(reinterpret_cast<const void*>(&_t1)) };
    QMetaObject::activate(this, &staticMetaObject, 4, _a);
}
QT_END_MOC_NAMESPACE
