#include <QCoreApplication>
#include <QSqlDatabase>
#include <QSqlQuery>
#include <QSqlError>
#include <QDebug>
#include <QStandardPaths>
#include <QDir>

int main(int argc, char *argv[]) {
    QCoreApplication app(argc, argv);
    
    // Find database
    QString dbPath = QStandardPaths::writableLocation(QStandardPaths::AppDataLocation) + "/fincept.db";
    qDebug() << "Looking for database at:" << dbPath;
    
    if (!QFile::exists(dbPath)) {
        // Try alternative location
        QString altPath = QStandardPaths::writableLocation(QStandardPaths::AppLocalDataLocation) + "/fincept.db";
        qDebug() << "Trying alternative path:" << altPath;
        if (QFile::exists(altPath)) {
            dbPath = altPath;
        } else {
            qDebug() << "Database not found!";
            return 1;
        }
    }
    
    qDebug() << "Database found at:" << dbPath;
    
    // Open database
    QSqlDatabase db = QSqlDatabase::addDatabase("QSQLITE");
    db.setDatabaseName(dbPath);
    
    if (!db.open()) {
        qDebug() << "Failed to open database:" << db.lastError().text();
        return 1;
    }
    
    // Query language setting
    QSqlQuery query(db);
    query.prepare("SELECT key, value, category FROM settings WHERE key LIKE '%language%' OR key LIKE '%appearance%'");
    
    if (query.exec()) {
        qDebug() << "\n=== Settings ===";
        while (query.next()) {
            qDebug() << query.value(0).toString() << "=" << query.value(1).toString() 
                     << "(category:" << query.value(2).toString() << ")";
        }
    } else {
        qDebug() << "Query failed:" << query.lastError().text();
    }
    
    db.close();
    return 0;
}
