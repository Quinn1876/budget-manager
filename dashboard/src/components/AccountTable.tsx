import EditIcon from "@/icons/Edit";
import { Account } from "@/types/account";
import Link from "next/link";

export default function AccountTable(props: {
    accounts: Account[],
    returnUri: string
}) {
    return (
        <table className="table-auto border-collapse border border-spacing-5">
            <thead>
            <tr>
                <th className="border px-4 py-2">Account Number</th>
                <th className="border px-4 py-2">Account Name</th>
                <th className="border px-4 py-2">Balance</th>
                <th className="border px-4 py-2">Account Type</th>
                <th className="border px-4 py-2">Account Owner</th>
            </tr>
            </thead>
            <tbody>
                {props.accounts.map((item: Account) => {
                    return (
                        <tr key={item.account_number}>
                            <td className="border p-2"><Link href={`/account/${item.account_number}`}>{item.account_number}</Link></td>
                            <td className="border p-2">{item.account_name}</td>
                            <td className="border p-2">{item.balance}</td>
                            <td className="border p-2">{item.account_type}</td>
                            <td className="border p-2">{item.owner}</td>
                            <td className="border"><Link href={`/account/edit/${item.account_number}?return=${props.returnUri}`}><EditIcon className="m-2"/></Link></td>
                        </tr>
                    );
                })}
            </tbody>
        </table>
    );
}
