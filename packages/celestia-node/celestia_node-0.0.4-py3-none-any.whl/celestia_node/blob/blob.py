from .types import BlobTypes

from typing import List


class Blob:

    def __init__(self, client: "Client") -> None:
        self.client = client

    def get(self, height: int, namespace: str, commitment: str) -> BlobTypes.BlobData:
        """
        Retrieves the blob by its commitment under the specified namespace and height.

        :param height: The blockchain height at which to retrieve the blob.
        :param namespace: The namespace of the blob.
        :param commitment: The commitment (Merkle subtree root) of the blob.
        :return: Response object containing the requested blob.
        """

        method = "blob.Get"

        return self.client.request(method, height=height, namespace=namespace, commitment=commitment)

    def get_all(self, height: int, namespaces: List[str]) -> List[BlobTypes.BlobData]:
        """
        Returns all blobs under the specified namespaces and height.

        :param height: The blockchain height at which to retrieve blobs.
        :param namespaces: A list of namespaces to retrieve blobs from.
        :return: Response object containing all the requested blobs.
        """

        method = "blob.GetAll"

        return self.client.request(method, height=height, namespaces=namespaces)

    def get_proof(self, height: int, namespace: str, commitment: str) -> BlobTypes.Proof:
        """
        Retrieves proofs of the blob in the given namespace at the specified height by commitment.

        :param height: The blockchain height for the proof retrieval.
        :param namespace: The namespace of the blob.
        :param commitment: The commitment of the blob.
        :return: Response object containing the proof of the blob.
        """

        method = "blob.GetProof"

        return self.client.request(method, height=height, namespace=namespace, commitment=commitment)

    def included(self, height: int, namespace: str, proof: BlobTypes.Proof, commitment: BlobTypes.Comitment) -> bool:
        """
        Checks whether a blob's given commitment is included at the given height and under the specified namespace.

        :param height: The blockchain height to check for inclusion.
        :param namespace: The namespace of the blob.
        :param proof: The proof of the blob.
        :param commitment: The commitment of the blob.
        :return: Boolean response indicating whether the blob is included.
        """

        method = "blob.Included"
        
        return self.client.request(method, height=height, namespace=namespace, proof=proof, commitment=commitment)

    def submit(self, blobs: List[BlobTypes.BlobData], options: BlobTypes.SubmitOptions) -> int:

        blobs = [blob.__dict__ for blob in blobs]
        options = options.__dict__

        method = "blob.Submit"

        return self.client.request(method, blobs, options)

