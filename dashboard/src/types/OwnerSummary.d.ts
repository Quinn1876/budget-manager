import { Account } from "./account";

interface OwnerSummary {
    owner: string;
    accounts: Account[];

    total_savings: number
    total_dept: number
}
