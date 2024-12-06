const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const dotenv = require('dotenv');
const cors = require('cors');
const connectDB = require('./config/db');
const authRoutes = require('./routes/authRoutes');
const Message = require('./models/Message');
const jwt = require('jsonwebtoken');

dotenv.config();

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

// Middleware
app.use(express.json());
app.use(cors());

// Connect to DB
connectDB();

// Auth Routes
app.use('/api/auth', authRoutes);

// Socket.io connection
let activeUsers = [];

io.on('connection', (socket) => {
  console.log('A user connected:', socket.id);

  socket.on('setUser', (token) => {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    activeUsers.push({ userId: decoded.userId, socketId: socket.id });
  });

  socket.on('sendMessage', async ({ senderId, receiverId, message }) => {
    const newMessage = new Message({
      sender: senderId,
      receiver: receiverId,
      message,
    });
    await newMessage.save();

    // Emit the message to the receiver
    const receiverSocket = activeUsers.find(user => user.userId.toString() === receiverId);
    if (receiverSocket) {
      io.to(receiverSocket.socketId).emit('receiveMessage', {
        senderId,
        message,
      });
    }
  });

  socket.on('disconnect', () => {
    activeUsers = activeUsers.filter(user => user.socketId !== socket.id);
    console.log('A user disconnected');
  });
});

const PORT = process.env.PORT || 5000;
server.listen(PORT, () => console.log(`Server running on port ${PORT}`));
