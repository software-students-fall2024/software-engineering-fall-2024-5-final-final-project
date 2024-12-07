# Chat Application - Node.js & MongoDB

A real-time chat application built with Node.js, MongoDB, Express, and Socket.io,. This application allows users to register, authenticate, and send/receive messages in real-time.

## Features
- **User Authentication**: Sign up and log in using JWT-based authentication.
- **Real-Time Messaging**: Users can send and receive messages instantly using Socket.io.
- **MongoDB Persistence**: All users and messages are stored in MongoDB.
- **User Profile**: Each user has a unique profile with their name, username, and avatar.
- **Private Messaging**: Users can send direct messages to other users.

## Technologies Used
- **Node.js**: JavaScript runtime for server-side logic.
- **Express**: Web framework for Node.js.
- **MongoDB**: Database for storing users and chat messages.
- **Mongoose**: MongoDB ODM to model and interact with data.
- **Socket.io**: Real-time communication between server and clients.
- **bcryptjs**: Password hashing.
- **jsonwebtoken (JWT)**: Token-based authentication.
- **cors**: Enable cross-origin resource sharing.
- **dotenv**: Environment variable management.

## Prerequisites
- Node.js (v12 or higher)
- MongoDB (locally or a cloud service like MongoDB Atlas)

## Installation

### 1. Clone the repository
```bash
cd chat-app
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory and add the following:

```env
PORT=5000
MONGO_URI=mongodb://localhost:27017/chat-app  # Change to your MongoDB URI if using Atlas
JWT_SECRET=mysecretkey  # Change this to a secure key
```

### 4. Start the Server
```bash
npm start
```

The server will run on `http://localhost:5000`.

### 5. Running in Development Mode
To start the server with auto-reloading (using nodemon):

```bash
npm run dev
```

## API Endpoints

### 1. **User Registration**  
- **POST** `/api/auth/register`
- **Description**: Registers a new user by providing a username, password, and optional avatar image.
- **Request Body**:
  ```json
  {
    "username": "john_doe",
    "password": "password123",
    "avatar": "https://link-to-avatar.jpg"
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "User created successfully",
      "user": {
        "id": "user_id",
        "username": "john_doe",
        "avatar": "https://link-to-avatar.jpg"
      }
    }
    ```
  - **400 Bad Request**: Missing fields or invalid data.

### 2. **User Login**  
- **POST** `/api/auth/login`
- **Description**: Logs in a user by providing a username and password, returns a JWT token.
- **Request Body**:
  ```json
  {
    "username": "john_doe",
    "password": "password123"
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Login successful",
      "token": "jwt_token_here"
    }
    ```
  - **401 Unauthorized**: Invalid credentials.

### 3. **Get User Profile**  
- **GET** `/api/users/me`
- **Description**: Retrieves the profile information of the currently logged-in user. This requires authentication via JWT token.
- **Headers**:
  - `Authorization: Bearer <JWT Token>`
- **Response**:
  - **200 OK**:
    ```json
    {
      "id": "user_id",
      "username": "john_doe",
      "avatar": "https://link-to-avatar.jpg"
    }
    ```
  - **401 Unauthorized**: Missing or invalid token.

### 4. **Send Message**  
- **POST** `/api/messages/send`
- **Description**: Sends a new message to another user.
- **Request Body**:
  ```json
  {
    "to": "receiver_user_id",
    "message": "Hello, how are you?"
  }
  ```
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "Message sent successfully",
      "message_data": {
        "from": "sender_user_id",
        "to": "receiver_user_id",
        "message": "Hello, how are you?",
        "timestamp": "2024-12-01T12:34:56Z"
      }
    }
    ```
  - **400 Bad Request**: Missing or invalid data.

### 5. **Get All Messages**  
- **GET** `/api/messages`
- **Description**: Retrieves all messages for the currently logged-in user. Requires authentication.
- **Headers**:
  - `Authorization: Bearer <JWT Token>`
- **Response**:
  - **200 OK**:
    ```json
    {
      "messages": [
        {
          "from": "sender_user_id",
          "to": "receiver_user_id",
          "message": "Hello, how are you?",
          "timestamp": "2024-12-01T12:34:56Z"
        },
        {
          "from": "receiver_user_id",
          "to": "sender_user_id",
          "message": "I'm good, thanks for asking!",
          "timestamp": "2024-12-01T12:35:30Z"
        }
      ]
    }
    ```
  - **401 Unauthorized**: Missing or invalid token.

### 6. **Real-Time Messaging with Socket.io**
- **Socket.io** enables real-time bidirectional communication between the server and clients.
- **Events**:
  - **Connect**: Client connects to the server.
  - **disconnect**: Client disconnects from the server.
  - **send_message**: Emit a message to the server.
  - **receive_message**: Listen for incoming messages.
  
  Example Client-Side Code:
  ```javascript
  const socket = io.connect('http://localhost:5000');

  // Send a message
  socket.emit('send_message', {
    to: 'receiver_user_id',
    message: 'Hello, this is a test message!'
  });

  // Listen for incoming messages
  socket.on('receive_message', (data) => {
    console.log('Received message:', data);
  });
  ```



