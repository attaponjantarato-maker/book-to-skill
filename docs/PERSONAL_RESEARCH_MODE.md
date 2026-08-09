# Personal Research Mode

This fork is being developed primarily as a personal, experimental knowledge system for medical imaging and nuclear medicine.

The default medical policy mode is therefore **advisory** rather than blocking:

- provenance and knowledge classes are retained because they improve retrieval and reasoning quality;
- technical/clinical caveats are returned as warnings;
- warnings do not prevent the agent from using the knowledge;
- `STRICT` mode remains available as an optional future setting for workflows that want hard operational gates.

This keeps the project lightweight and useful for learning, experimentation, prototyping, and research workflow design without turning the knowledge layer into a clinical-production compliance system.
