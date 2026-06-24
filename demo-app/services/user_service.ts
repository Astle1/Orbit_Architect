// import { queryDatabase } from "../database/client";
import { logInfo } from "../utils/logger";

export function fetchUserData() {
    logInfo("Fetching user...");
    queryDatabase("SELECT * FROM users");
}
