import sqlite3

DB_NAME = "inventory_chatbot.db"

def create_schema(cursor):
    tables = [
        """
        CREATE TABLE Customers(
            CustomerId INTEGER PRIMARY KEY AUTOINCREMENT,
            CustomerCode TEXT UNIQUE NOT NULL,
            CustomerName TEXT NOT NULL,
            Email TEXT,
            Phone TEXT,
            BillingAddress1 TEXT,
            BillingCity TEXT,
            BillingCountry TEXT,
            CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt DATETIME,
            IsActive INTEGER NOT NULL DEFAULT 1
        );
        """,
        """
        CREATE TABLE Vendors(
            VendorId INTEGER PRIMARY KEY AUTOINCREMENT,
            VendorCode TEXT UNIQUE NOT NULL,
            VendorName TEXT NOT NULL,
            Email TEXT,
            Phone TEXT,
            AddressLine1 TEXT,
            City TEXT,
            Country TEXT,
            CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt DATETIME,
            IsActive INTEGER NOT NULL DEFAULT 1
        );
        """,
        """
        CREATE TABLE Sites(
            SiteId INTEGER PRIMARY KEY AUTOINCREMENT,
            SiteCode TEXT UNIQUE NOT NULL,
            SiteName TEXT NOT NULL,
            AddressLine1 TEXT,
            City TEXT,
            Country TEXT,
            TimeZone TEXT,
            CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt DATETIME,
            IsActive INTEGER NOT NULL DEFAULT 1
        );
        """,
        """
        CREATE TABLE Locations(
            LocationId INTEGER PRIMARY KEY AUTOINCREMENT,
            SiteId INTEGER NOT NULL,
            LocationCode TEXT NOT NULL,
            LocationName TEXT NOT NULL,
            ParentLocationId INTEGER,
            CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt DATETIME,
            IsActive INTEGER NOT NULL DEFAULT 1,
            CONSTRAINT UQ_Locations_SiteCode UNIQUE (SiteId, LocationCode),
            CONSTRAINT FK_Locations_Site FOREIGN KEY (SiteId) REFERENCES Sites(SiteId),
            CONSTRAINT FK_Locations_Parent FOREIGN KEY (ParentLocationId) REFERENCES Locations(LocationId)
        );
        """,
        """
        CREATE TABLE Items(
            ItemId INTEGER PRIMARY KEY AUTOINCREMENT,
            ItemCode TEXT UNIQUE NOT NULL,
            ItemName TEXT NOT NULL,
            Category TEXT,
            UnitOfMeasure TEXT,
            CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt DATETIME,
            IsActive INTEGER NOT NULL DEFAULT 1
        );
        """,
        """
        CREATE TABLE Assets(
            AssetId INTEGER PRIMARY KEY AUTOINCREMENT,
            AssetTag TEXT UNIQUE NOT NULL,
            AssetName TEXT NOT NULL,
            SiteId INTEGER NOT NULL,
            LocationId INTEGER,
            SerialNumber TEXT,
            Category TEXT,
            Status TEXT NOT NULL DEFAULT 'Active',
            Cost REAL,
            PurchaseDate DATE,
            VendorId INTEGER,
            CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt DATETIME,
            CONSTRAINT FK_Assets_Site FOREIGN KEY (SiteId) REFERENCES Sites(SiteId),
            CONSTRAINT FK_Assets_Location FOREIGN KEY (LocationId) REFERENCES Locations(LocationId),
            CONSTRAINT FK_Assets_Vendor FOREIGN KEY (VendorId) REFERENCES Vendors(VendorId)
        );
        """,
        """
        CREATE TABLE Bills(
            BillId INTEGER PRIMARY KEY AUTOINCREMENT,
            VendorId INTEGER NOT NULL,
            BillNumber TEXT NOT NULL,
            BillDate DATE NOT NULL,
            DueDate DATE,
            TotalAmount REAL NOT NULL,
            Currency TEXT NOT NULL DEFAULT 'USD',
            Status TEXT NOT NULL DEFAULT 'Open',
            CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt DATETIME,
            CONSTRAINT UQ_Bills_Vendor_BillNumber UNIQUE (VendorId, BillNumber),
            CONSTRAINT FK_Bills_Vendor FOREIGN KEY (VendorId) REFERENCES Vendors(VendorId)
        );
        """,
        """
        CREATE TABLE PurchaseOrders (
            POId INTEGER PRIMARY KEY AUTOINCREMENT,
            PONumber TEXT NOT NULL,
            VendorId INTEGER NOT NULL,
            PODate DATE NOT NULL,
            Status TEXT NOT NULL DEFAULT 'Open',
            SiteId INTEGER,
            CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt DATETIME,
            CONSTRAINT UQ_PurchaseOrders_Number UNIQUE (PONumber),
            CONSTRAINT FK_PurchaseOrders_Vendor FOREIGN KEY (VendorId) REFERENCES Vendors(VendorId),
            CONSTRAINT FK_PurchaseOrders_Site FOREIGN KEY (SiteId) REFERENCES Sites(SiteId)
        );
        """,
        """
        CREATE TABLE PurchaseOrderLines(
            POLineId INTEGER PRIMARY KEY AUTOINCREMENT,
            POId INTEGER NOT NULL,
            LineNumber INTEGER NOT NULL,
            ItemId INTEGER,
            ItemCode TEXT NOT NULL,
            Description TEXT,
            Quantity REAL NOT NULL,
            UnitPrice REAL NOT NULL,
            CONSTRAINT UQ_PurchaseOrderLines UNIQUE (POId, LineNumber),
            CONSTRAINT FK_PurchaseOrderLines_PO FOREIGN KEY (POId) REFERENCES PurchaseOrders(POId),
            CONSTRAINT FK_PurchaseOrderLines_Item FOREIGN KEY (ItemId) REFERENCES Items(ItemId)
        );
        """,
        """
        CREATE TABLE SalesOrders(
            SOId INTEGER PRIMARY KEY AUTOINCREMENT,
            SONumber TEXT NOT NULL,
            CustomerId INTEGER NOT NULL,
            SODate DATE NOT NULL,
            Status TEXT NOT NULL DEFAULT 'Open',
            SiteId INTEGER,
            CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt DATETIME,
            CONSTRAINT UQ_SalesOrders_Number UNIQUE (SONumber),
            CONSTRAINT FK_SalesOrders_Customer FOREIGN KEY (CustomerId) REFERENCES Customers(CustomerId),
            CONSTRAINT FK_SalesOrders_Site FOREIGN KEY (SiteId) REFERENCES Sites(SiteId)
        );
        """,
        """
        CREATE TABLE SalesOrderLines(
            SOLineId INTEGER PRIMARY KEY AUTOINCREMENT,
            SOId INTEGER NOT NULL,
            LineNumber INTEGER NOT NULL,
            ItemId INTEGER,
            ItemCode TEXT NOT NULL,
            Description TEXT,
            Quantity REAL NOT NULL,
            UnitPrice REAL NOT NULL,
            CONSTRAINT UQ_SalesOrderLines UNIQUE (SOId, LineNumber),
            CONSTRAINT FK_SalesOrderLines_SO FOREIGN KEY (SOId) REFERENCES SalesOrders(SOId),
            CONSTRAINT FK_SalesOrderLines_Item FOREIGN KEY (ItemId) REFERENCES Items(ItemId)
        );
        """
    ]

    for table in tables:
        cursor.execute(table)
    print(f"Successfully executed {len(tables)} schema statements.")


def seed_data(cursor):
    print("Seeding initial data...")

    customers = [
        (
            "CUST-EGY-01",
            "Nile Tech Solutions",
            "contact@niletech.eg",
            "+20-100-555-0100",
            "10 Talaat Harb St",
            "Cairo",
            "Egypt",
        ),
        (
            "CUST-EGY-02",
            "Alexandria Importers",
            "info@aleximporters.eg",
            "+20-120-555-0101",
            "45 Corniche Road",
            "Alexandria",
            "Egypt",
        ),
    ]
    cursor.executemany(
        """
        INSERT INTO Customers (CustomerCode, CustomerName, Email, Phone, BillingAddress1, BillingCity, BillingCountry)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        customers,
    )

    # 2. Vendors
    vendors = [
        (
            "VEND-EGY-01",
            "Cairo Electronics Group",
            "sales@cairoelectronics.eg",
            "+20-111-555-0200",
            "90th Street North",
            "New Cairo",
            "Egypt",
        ),
        (
            "VEND-EGY-02",
            "Maadi Office Supplies",
            "orders@maadioffice.eg",
            "+20-100-555-0201",
            "Road 9",
            "Maadi",
            "Egypt",
        ),
    ]
    cursor.executemany(
        """
        INSERT INTO Vendors (VendorCode, VendorName, Email, Phone, AddressLine1, City, Country)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        vendors,
    )

    # 3. Sites
    sites = [
        (
            "SITE-CAIRO-HQ",
            "Cairo Headquarters",
            "1 Tahrir Square",
            "Cairo",
            "Egypt",
            "EET",
        ),
        (
            "SITE-ALEX-WH",
            "Alexandria Warehouse",
            "Borg El Arab",
            "Alexandria",
            "Egypt",
            "EET",
        ),
    ]
    cursor.executemany(
        """
        INSERT INTO Sites (SiteCode, SiteName, AddressLine1, City, Country, TimeZone)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        sites,
    )

    # 4. Locations
    locations = [
        (1, "CAI-HQ-FL1", "HQ Floor 1 (General Office)", None),
        (2, "ALX-WH-A", "Warehouse Zone A", None),
        (2, "ALX-WH-B", "Warehouse Zone B", None),
    ]
    cursor.executemany(
        "INSERT INTO Locations (SiteId, LocationCode, LocationName, ParentLocationId) VALUES (?, ?, ?, ?)",
        locations,
    )

    # 5. Items
    items = [
        ("ITM-001", 'MacBook Pro 16"', "Electronics", "EA"),
        ("ITM-002", "Ergonomic Office Chair", "Furniture", "EA"),
    ]
    cursor.executemany(
        "INSERT INTO Items (ItemCode, ItemName, Category, UnitOfMeasure) VALUES (?, ?, ?, ?)",
        items,
    )

    # 6. Assets
    assets = [
        (
            "AST-EGY-0001",
            "Laptop-Asser",
            1,
            1,
            "M2P-987654",
            "Electronics",
            "Active",
            65000.00,
            "2024-11-01",
            1,
        ),
        (
            "AST-EGY-0002",
            "Chair-Asser",
            1,
            1,
            "CHR-123456",
            "Furniture",
            "Active",
            12000.00,
            "2025-01-20",
            2,
        ),
    ]
    cursor.executemany(
        """
        INSERT INTO Assets (AssetTag, AssetName, SiteId, LocationId, SerialNumber, Category, Status, Cost, PurchaseDate, VendorId)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        assets,
    )

    print("Data seeding completed successfully.")


def main():
    print(f"Creating and setting up new database: {DB_NAME}")
    conn = sqlite3.connect(DB_NAME)

    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        create_schema(cursor)
        seed_data(cursor)
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()

    print("Database setup finished.")


if __name__ == "__main__":
    main()
