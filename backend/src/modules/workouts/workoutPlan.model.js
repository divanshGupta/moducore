import mongoose from "mongoose";

const exerciseSchema = new mongoose.Schema(
  {
    name: String,
    sets: Number,
    reps: String,
    rest: String,
  },
  { _id: false }
);

const workoutDaySchema = new mongoose.Schema(
  {
    day: {
      type: String, // Monday, Tuesday
    },
    exercises: [exerciseSchema],
  },
  { _id: false }
);

const workoutPlanSchema = new mongoose.Schema(
  {
    user: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User",
      required: true,
    },

    trainer: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User",
    },

    title: String,
    days: [workoutDaySchema],
  },
  { timestamps: true }
);

export default mongoose.model("WorkoutPlan", workoutPlanSchema);
