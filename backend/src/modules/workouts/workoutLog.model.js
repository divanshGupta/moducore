import mongoose from "mongoose";

const logExerciseSchema = new mongoose.Schema(
  {
    name: String,
    sets: Number,
    reps: String,
    weight: Number,
  },
  { _id: false }
);

const workoutLogSchema = new mongoose.Schema(
  {
    user: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User",
    },

    date: String, // YYYY-MM-DD

    exercises: [logExerciseSchema],

    completed: {
      type: Boolean,
      default: true,
    },
  },
  { timestamps: true }
);

export default mongoose.model("WorkoutLog", workoutLogSchema);
