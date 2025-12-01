from build_connection import BuildConnection
db = BuildConnection()

class TableManipulation:
    def __init__(self):
        self.conn, self.cursor = db.make_connection()

    def insert_initial_data(self):
        """Inserts required preliminary data for testing the trigger."""
        try:
            # 1. Insert a Course
            self.cursor.execute("INSERT INTO course VALUES ('CS101', 'Intro to Computing');")

            # 2. Insert Staff (REQUIRED for the trigger check)
            # Staff A: Welfare Role (Correct)
            self.cursor.execute("INSERT INTO users VALUES ('S0000001', 'welfare_staff', 'welfare@uni.edu');")
            # Staff B: Module Role (Correct)
            self.cursor.execute("INSERT INTO users VALUES ('S0000002', 'module_staff', 'module@uni.edu');")
            # Staff C: *Incorrect* Role - used for failure test
            self.cursor.execute("INSERT INTO users VALUES ('S0000003', 'welfare_staff', 'wrong@uni.edu');") 
            
            self.conn.commit()
            print("\n✅ Initial Test Data Inserted.")
        except Exception as e:
            # Catching "Duplicate entry" if run multiple times
            if "Duplicate entry" in str(e):
                print("\n⚠️ Initial Test Data already exists.")
            else:
                raise e

    def test_module_trigger(self):
        self.insert_initial_data()
        
        # --- TEST 1: SUCCESSFUL INSERT (Correct Roles) ---
        try:
            print("\n--- Running Test 1: Correct Roles ---")
            self.cursor.execute("""
                INSERT INTO module 
                VALUES ('MOD001', 'Programming Basics', 'CS101', 1, 'S0000001', 'S0000002');
            """)
            self.conn.commit()
            print("✅ SUCCESS: Module MOD001 inserted correctly. (Trigger passed)")
        except Exception as e:
            print(f"❌ FAIL: Test 1 failed unexpectedly: {e}")

        # --- TEST 2: FAILED INSERT (Invalid Module Staff Role) ---
        try:
            print("\n--- Running Test 2: Invalid Module Staff ---")
            # Attempt to use S0000003 (welfare staff) as module_staff_id
            self.cursor.execute("""
                INSERT INTO module 
                VALUES ('MOD002', 'Advanced DB', 'CS101', 2, 'S0000001', 'S0000003');
            """)
            self.conn.commit()
            print("❌ FAIL: Insert should have been blocked by the trigger, but committed.")
        except Exception as e:
            # The trigger throws a SQLSTATE '45000' error
            if "Invalid module_staff_id" in str(e):
                print(f"✅ SUCCESS: Trigger blocked insertion with error: {e.args[0]}")
                # Rollback the failed transaction
                self.conn.rollback() 
            else:
                print(f"❌ FAIL: Test 2 failed with unexpected error: {e}")


manipulator = TableManipulation()
manipulator.test_module_trigger()