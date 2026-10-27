import csv
import os
from datetime import datetime

from mip import BINARY, Model, OptimizationStatus, xsum

from person import Gender, Person
from src.rooms.rooms import Room


def form_rooms(
    people: dict[str, Person],
    rooms: list[Room],
    is_printing_output,
    args_output_file,
    args_no_output,
    args_verbose,
    args_timeout,
):
    """Assign campers to nonempty, single-gender rooms using Gurobi."""
    if not rooms:
        raise ValueError("At least one room is required.")

    campers = list(people.values())
    if any(c.gender not in (Gender.MALE, Gender.FEMALE) for c in campers):
        raise ValueError("Every camper must have a male or female gender.")

    camper_ids = range(len(campers))
    room_ids = range(len(rooms))

    # Python-MIP builds the mixed integer model; Gurobi solves it.
    m = Model(name="room_formation", solver_name="GRB")
    print(f"Using solver: {m.solver_name}")
    m.verbose = 1 if args_verbose else 0
    m.max_seconds = args_timeout

    # x[c][r] is 1 exactly when camper c is assigned to room r.
    x = [[m.add_var(var_type=BINARY) for r in room_ids] for c in camper_ids]
    # A room's binary gender is 1 for male and 0 for female.
    room_is_male = [m.add_var(var_type=BINARY) for r in room_ids]

    for c in camper_ids:
        # Every camper must be assigned to exactly one room.
        m += xsum(x[c][r] for r in room_ids) == 1
        for r in room_ids:
            # Sharing one gender variable prevents mixed-gender occupancy.
            if campers[c].gender == Gender.MALE:
                m += x[c][r] <= room_is_male[r]
            else:
                m += x[c][r] <= 1 - room_is_male[r] # type: ignore

    for r in room_ids:
        # Every requested room must contain at least one camper.
        m += xsum(x[c][r] for c in camper_ids) >= 1  # type: ignore[operator]
        # The room CSV defines the number of available beds.
        m += xsum(x[c][r] for c in camper_ids) <= rooms[r].capacity

    # Find any assignment satisfying gender and bed-capacity constraints.
    m.optimize()

    print(f"Total dataset size: {len(campers)}")
    print(f"Total rooms: {len(rooms)}")

    # A feasible solution still satisfies the rules if the time limit expires.
    if m.status in (OptimizationStatus.OPTIMAL, OptimizationStatus.FEASIBLE):
        for r in room_ids:
            bed_index = 0
            for c in camper_ids:
                assignment = x[c][r].x
                if assignment is not None and float(assignment) >= 0.99:
                    # Person has no room setter, so store the room locally here.
                    campers[c].room = rooms[r].id
                    # Assign each occupant a distinct bed from the room's list.
                    campers[c].bed = rooms[r].beds[bed_index]
                    bed_index += 1

        if args_no_output is not True:
            output_dir = args_output_file if args_output_file is not None else "output"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            output_path = os.path.join(output_dir, f"rooms_{timestamp}.csv")

            with open(output_path, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(
                    ["ID", "First name", "Last name", "Room", "Sleeping arrangement"]
                )
                writer.writerows(
                    [c.uuid, c.first_name, c.last_name, c.room,
                     f"{c.bed.name.title()} bunk" if c.bed is not None else "Unassigned"]
                    for c in campers
                )

            print(f"Output saved to: {output_path}")

        if is_printing_output:
            for room in rooms:
                room_members = [c for c in campers if c.room == room.id]
                print(f"\n{room.name} - Total: {len(room_members)}")
                for member in room_members:
                    print(
                        f"  {member.first_name} {member.last_name}"
                        f" - {member.bed.name.title() + ' bunk' if member.bed is not None else 'Unassigned'}"
                    )

        return campers

    print("No feasible room assignment found.")
    return None
