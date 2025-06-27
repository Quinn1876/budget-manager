import AccountTable from "@/components/AccountTable";
import { getClient } from "@/lib/client";
import { gql } from "@apollo/client";

const query = gql`
  query GetAllAccounts {
    listAccounts {
      account_number
      account_type
      owner
      account_name
    }
}`;

export default async function Home() {
  const client = getClient();
  const { data } = await client.query({ query });
  return (
    <div className="flex pl-4 pt-4">
      <AccountTable accounts={data["listAccounts"]}/>
    </div>
  );
}
