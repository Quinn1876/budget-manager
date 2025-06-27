import AccountBalancePieChart from "@/components/AccountBalancePieChart";
import { getClient } from "@/lib/client";
import { OwnerSummary } from "@/types/OwnerSummary";
import { gql } from "@apollo/client";

const query = gql`
  query GetOwnerSummary($owner: String!) {
    getOwnerSummary(owner: $owner) {
      owner
      accounts {
        account_name
        balance
        account_type
      }
      total_savings
      total_dept
    }
  }
`;

export default async function OwnerSummaryPage(props: {
  params: Promise<{ owner: string }>;
}) {
  const {
    data: { getOwnerSummary },
    loading,
    error,
  } = await getClient().query<{ getOwnerSummary: OwnerSummary }>({
    query,
    variables: {
      owner: (await props.params).owner,
    },
  });

  if (loading) {
    return <h1>Loading Owner Page...</h1>;
  }
  if (error) {
    console.error(error);
    return <h1>Error</h1>;
  }
  return (
    <div className="flex grow w-full h-dvh align-middle justify-center">
      <div className="bg-gray-500 w-4xl mt-8 mb-8 p-8 rounded-mg flex flex-col">
        <h1>{getOwnerSummary.owner}&apos;s Dashboard</h1>
        <div className="flex flex-col self-center min-w-full min-h-1/2 bg-white drop-shadow-2xl rounded-2xl p-4">
          <h2 className="text-black">Total Savings: {getOwnerSummary.total_savings}</h2>
          <AccountBalancePieChart textColor="black" width="100%" height="100%" accounts={getOwnerSummary.accounts.filter((account) => account.account_type == "Savings")} />
        </div>
      </div>
    </div>
  );
}
