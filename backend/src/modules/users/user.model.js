import mongoose from "mongoose";

const userSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: true,
      trim: true,
    },

    email: {
      type: String,
      required: true,
      unique: true,
      lowercase: true,
    },

    password: {
      type: String,
      required: true,
      select: false, // 🔐 critical for security
    },

    role: {
      type: String,
      enum: ["admin", "trainer", "member"],
      default: "member",
    },

    phone: String,

    trainer: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User", // trainer is also a user
    },

    height: Number,
    weight: Number,
    goal: {
      type: String,
      enum: ["fat_loss", "muscle_gain", "maintenance"],
    },

    isActive: {
      type: Boolean,
      default: true,
    },
  },
  { timestamps: true }
);

export default mongoose.model("User", userSchema);
