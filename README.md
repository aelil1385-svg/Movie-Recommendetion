# 🎬 Movie Recommendation Project - Complete Setup Guide

## **📋 Prerequisites**
- ✅ Python 3.9+ installed
- ✅ Virtual environment activated
- ✅ TMDB API key obtained

---

## **🚀 Step 1: Project Setup**

### **1.1 Navigate to Project Directory**
```bash
cd Movie-Recommendetion
```

### **1.2 Activate Virtual Environment**
```bash
source venv/bin/activate
```

### **1.3 Install Dependencies**
```bash
pip install -r requirements.txt
```
---

## **🎬 Step 2: Start the Application**

### **2.1 Run the App**
```bash
streamlit run app.py
```

### **2.2 Access the App**
- **URL**: `http://localhost:8501`
- **Auto-opens**: Should open automatically in your browser

---

## **👤 Step 3: User Registration (Sign Up)**

### **3.1 Navigate to Sign Up**
1. **Open the app** in your browser
2. **Click the "Sign up" tab** (next to "Log in")

### **3.2 Fill Out Registration Form**
- **Full name**: Enter your name (e.g., "John Doe")
- **Email**: Enter a valid email (e.g., "john@example.com")
- **Password**: Create a password (minimum 6 characters)
- **Confirm password**: Re-enter the same password

### **3.3 Submit Registration**
1. **Click "Create account"** button
2. **Success message** should appear
3. **You'll be automatically logged in**

---

## **🔐 Step 4: User Login**

### **4.1 Log Out First (to test login)**
1. **Click "Log out"** button in the sidebar
2. **You'll be redirected** to the login page

### **4.2 Log In**
1. **Click the "Log in" tab**
2. **Enter your credentials**:
   - **Email**: Use the email you registered with
   - **Password**: Use the password you created
3. **Click "Log in"** button
4. **Success**: You'll be redirected to the movie browser

---

## **🎭 Step 5: Explore Movie Features**

### **5.1 Browse Movies**
- **Trending**: See popular movies
- **Search**: Find specific movies
- **Actor**: Browse movies by actor
- **Genre**: Explore by movie genre

### **5.2 Movie Details**
- **Click movie posters** to watch trailers
- **Click "View details & trailer"** for full information

---

## **🛠️ Troubleshooting**

### **Common Issues:**

**❌ "TMDB_API_KEY is not set"**
- **Solution**: Check your `.env` file has the correct API key

**❌ "No account found with that email"**
- **Solution**: Make sure you're using the exact email from registration

**❌ "Incorrect password"**
- **Solution**: Check password spelling and case sensitivity

**❌ Port already in use**
- **Solution**: Streamlit will automatically use the next available port

**❌ Database errors**
- **Solution**: The database creates automatically - no setup needed

---

## **📱 Alternative: Guest Mode**

If you don't want to create an account:
1. **Click "Continue as Guest"** tab
2. **Click "Continue as Guest"** button
3. **Browse movies** without registration

---

## **🎯 Success Indicators**

✅ **App starts** without errors  
✅ **Login page** displays with 50% width container  
✅ **Sign up** creates account successfully  
✅ **Login** works with registered credentials  
✅ **Movie browsing** shows real data from TMDB  
✅ **Database** stores user information automatically  

---

## **🔧 Development Notes**

- **Auto-reload**: Changes to code automatically refresh the app
- **Database**: SQLite file (`app.db`) created automatically
- **Session**: User stays logged in during browser session
- **Responsive**: Works on desktop and mobile devices

**Ready to explore movies!** 🎬✨