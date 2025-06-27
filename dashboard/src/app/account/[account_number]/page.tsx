import AccountForm from "@/components/AccountForm";
import { getClient } from "@/lib/client";
import { Account } from "@/types/account";
import { gql } from "@apollo/client";

const query = gql`
  query GetAccount($account_number: String!) {
    getAccount(account_number: $account_number) {
      balance,
      owner,
      account_type,
      account_number,
      initial_balance,
      account_name
    }
  }
`

export default async function ViewAccountPage({
    params,
}: {
    params: Promise<{account_number: string}>
}) {
    const { data, loading, error } = await getClient().query<{getAccount: Account}>({ query, variables: {
        account_number: (await params).account_number
    } });

    if (loading) {
      return <p>Loading</p>
    }
    if (error) {
      return <p>Error Occurred</p>
    }

    return (
        <div className="flex grow w-full h-dvh align-middle justify-center">
          <div className="bg-gray-500 w-4xl mt-8 mb-8 p-8 rounded-mg">
            {/* <AccountForm account={data.getAccount}/> */}
          </div>
        </div>
    )
}
